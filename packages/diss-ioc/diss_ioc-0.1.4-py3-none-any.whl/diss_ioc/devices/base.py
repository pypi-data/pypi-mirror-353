#!/usr/bin/python3

import enum, logging, traceback, asyncio, sys, inspect, time, pprint, \
    os

from uuid import uuid4

from collections.abc import Iterable, Mapping
from functools import partial

from diss_ioc.frame import FrameCollector

from diss_ioc.event import Command, CommandRequest, QueryRequest

logger = logging.getLogger(__name__)

from diss_ioc.event import *
from diss_ioc.event import _Command_i2n

__all__ = [
    "command_handler",
    "query_handler",
    "event_handler",
    "command_task",
    "DeviceEngineBase"
]

def _generic_event_handler(event_type, *value_list, param_name=None):
    # Generic decorator for event handlers.
    # See also DetectorEngine.distpach_event() for details.
    def func_wrapper(func):
        def event_wrapper(self, event):
            return func(self, event)
        event_wrapper._emeta_ = (event_type, param_name, value_list)
        return event_wrapper
    return func_wrapper

def command_handler(*command_ids):
    return _generic_event_handler(CommandRequest, *command_ids, param_name='command')

def query_handler(*query_ids):
    return _generic_event_handler(QueryRequest, *query_ids, param_name='query')

def event_handler(event_type):
    return _generic_event_handler(event_type, param_name=None)

def command_task(command):
    # Decorator for detector command tasks. Use as @command_task(Command.Acquire)
    def func_wrapper(func):
        #return func(command)
        def task_wrapper(self, **command_args):
            return func(self, command, **command_args)
        task_wrapper._cmd_task_meta_ = (command,)
        return task_wrapper
    return func_wrapper

class DeviceEngineMeta(type):

    ## Metaclas for DeviceEngine (takes care of all
    ## @command... and @query... handlers)
    
    def __new__(cls, name, bases, nspace, *init_args, **init_kw):
        nspace['_event_handlers'] = evhan = {}
        nspace['_task_handlers']  = tahan = {}
        for n,obj in nspace.items():
            if hasattr(obj, '_emeta_'):
                evhan[obj._emeta_] = obj
            if hasattr(obj, '_cmd_task_meta_'):
                tahan[obj._cmd_task_meta_] = obj
        return super().__new__(cls, name, bases, nspace)


class DeviceEngineBase(metaclass=DeviceEngineMeta):
    '''
    DetectorEngine base class for the DEVICE role.
    '''

    def __init__(self, queue, args=None, env=None, period=0.01):
        super().__init__()
        self._args = args if args is not None else sys.argv.copy()
        self._env = env if env is not None else os.environ.copy()
        self._events = queue
        self._period = period
        self._action_task_pool = {}


    async def dispatch_event(self, event, raise_on_miss=False, raise_on_error=True):

        # Calls the registerd event handler.
        # The dictionary of event handlers is:
        #
        #     self._handlers = {
        #         (EventType, param_name, value_list): proc,
        #         ...
        #     }
        #
        # with the following meaning:
        #  - EventType: the type of event we're handling (typically
        #    a specific `CommandRequest` or `QueryRequest`
        #
        #  - param_name: a string naming a specific property of that
        #    particular event (e.g. "command" for a `CommandRequest`)
        #    Can also be `None`, in which case the event is accepted
        #    as-is
        # 
        #  - value_list: a list/tuple of accepted values for `param_name`
        #

        try:
            for edata,func in self._event_handlers.items():

                event_type, param_name, value_list = edata

                if not isinstance(event, event_type):
                    continue

                # if param_name is None, we accept.
                # if event."value" is None, we also accept.
                if (param_name is not None):
                    val = getattr(event, param_name)
                    if (val is not None) and \
                       (len(value_list) > 0) and \
                       (val not in value_list):
                        continue
                try:
                    hr = func(self, event)

                    if inspect.iscoroutine(hr):
                        return await hr

                except Exception as e:
                    logger.error(f'event="{event}" handler="{func}" '
                                 f'msg="Handler raised exception" error="{e}"')
                    if raise_on_error:
                        raise e

                return hr

            if raise_on_miss:
                raise RuntimeError(f'event="{event}" msg="No handler"')
            
        except Exception as e:
            print(f'Error processing {event}: {e}')
            raise


    async def _task_guard_and_cleanup(self, cmd):

        ## Makes sure that no other task with the same command 'cmd'
        ## is currently running
        task = self._action_task_pool.get(cmd, None)

        if (task is not None):
            if not task.done():
                #raise CommandException(CommandResultState(cmd, CommandResult.Failed,
                #                                          detail="Command already in progress"))
                logger.warning(f'msg="Should be finished, but task still running; this might block" '
                               f'command="{cmd}"')
                
            try:
                #task.cancel() ## not necessary, should end by itself
                await task

            except asyncio.CancelledError as e:
                pass

            except Exception as e:
                # It's too late now, the task is long gone. Catch, log, ignore.
                logger.error(f'msg="Task previously raised an error" '
                             f'error={e} task="{task}"')


    def _task_done_callback(self, cmd, task, ctx=None):
        exc = task.exception()
        if exc is not None:
            logger.error(f'msg="Command task failed" '
                         f'command={_Command_i2n[cmd]} '
                         f'detail="{exc}"')
            self.push_event(ErrorEvent(exc, fail=True))


    async def _task_kill(self, cmd, msg=None):
        ## Shoots down the task for command 'cmd' and waits for completion
        task = self._action_task_pool.get(cmd, None)
        if task is not None:
            task.cancel(msg)
            with suppress(asyncio.CancelledError):
                await task


    def _find_command_handler(self, cmd):
        for spec,proc in self._task_handlers.items():
            if spec[0] == cmd:
                return proc

        raise RuntimeError(f'msg="Incomplete device backend, task not defined" '
                           f'command="{_Command_i2n[cmd]}" '
                           f'device="{self.__class__.__name__}"')


    async def dispatch_command(self, event):
        # Generic command handler. Requires a local coroutine to start
        # an asyncio task on, which handles the command top-to-bottom
        # and generates the appropriate events.
        #
        # In subclasses, this subroutine is marked by the `@command_task(...)`
        # decorator and needs to have the signaure `async def proc(self, cmd, ...)`
        # with any specific command parameters coming in as named kwargs.
        
        try:
            await self._task_guard_and_cleanup(event.command)
            
            proc = self._find_command_handler(event.command)
            
            self._action_task_pool[event.command] = \
                asyncio.Task(proc(self, **(event.params)), eager_start=False, name=f'{event}')

            self._action_task_pool[event.command].add_done_callback(
                partial(self._task_done_callback, event.command)
            )

            return CommandResultState(event.command, CommandResult.Success)

        except CommandException as e:
            return e.command_result
        
        except Exception as e:
            return CommandResultState(event.command, CommandResult.Failed,
                                      detail=f'{e}')


    def push_event(self, ev):
        self._events.push(ev)


    async def step(self, raise_on_error=True):
        '''
        Executes one single event-processing step.
        '''

        try:
            event = self._events.pop_role(DetectorEngineRole.DEVICE, raise_empty=False)
            if isinstance(event, CommandRequest):
                new_events = await self.dispatch_command(event)
            else:
                new_events = await self.dispatch_event(event)

            if new_events is not None:
                self._events.push(new_events)

        except Exception as e:
            logger.error(f'msg="Error in event processing, details follow"')
            logger.error(f'event={event}')            
            logger.error(f'detail="{str(e)}"')
            logger.error(traceback.print_exc())
            if raise_on_error:
                raise
        

    async def run(self, period=None, stop_on_fail=True, raise_on_fail=False):
        '''
        Runs an event processing loop indefinitely.
        '''
        
        if period is None:
            period = self._period
            
        while True:
            try:
                await asyncio.gather(self.step(),
                                     asyncio.sleep(period),
                                     return_exceptions=False)
            except Exception as e:
                logger.error(f'msg="Detector engine failed, details follow"')
                logger.error(e)
                logger.error(traceback.format_exc())
                if raise_on_fail:
                    raise
                if stop_on_fail:
                    break


