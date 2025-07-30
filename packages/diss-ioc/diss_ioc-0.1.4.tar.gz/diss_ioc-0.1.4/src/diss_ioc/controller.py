import enum, logging, traceback, asyncio, sys, inspect, time, pprint, os

from uuid import uuid4

from collections.abc import Iterable, Mapping
from functools import partial

from diss_ioc.frame import FrameCollector
from diss_ioc.event import *
from diss_ioc.event import _Command_i2n

logger = logging.getLogger(__name__)


'''
Implements a (generic?) Detector state machine.

The state machine is an abstraction layer between two roles: the Device,
doing all the imaging work; and the Controller, making the decision and
sending commands to the Device.
'''

_valid_states = {
    getattr(DetectorState, k) \
    for k in filter(lambda i: not i.startswith('_'),
                    DetectorState.__dict__)
}

_state_names = {
    getattr(DetectorState, k):k \
    for k in filter(lambda i: not i.startswith('_'),
                    DetectorState.__dict__)
}

class StateHooks:
    '''
    Manages a list of per-state hooks.
    '''
    
    def __init__(self, state_enum):
        self._state_names = {
            k for k in filter(lambda n: not n.startswith('_'), state_enum.__dict__)
        }
        
        self._state_ids = {
            getattr(state_enum, n) for n in self._state_names
        }
        
        self._hooks = {
            i:[] for i in self._state_ids
        }


    def remove(self, obj_list):
        for sid, sproc in obj_list.items():
            self_hooks[sid].remove(sproc)


    def add_hook(self, proc, when_in=None, when_not_in=None):
        '''
        Adds a hook to be called when the corresponding state is entered.
        The hook is of the signature `def proc(state, entering)`,\
        with `entering` being a boolean that is `True` once per state-cycle,
        when the corresponding state is being transitioned into.

        The hook function may be a coroutine (asyncio), in which case it will
        be awaited for.

        Hooks are only handled inside this object's own `.run()` method. If you're
        implementing your own loop, by stepping through the states using the
        (non-blocking) `.state_proc()`, then you need to take care of the hooks
        yourself. The `add_hook()` / `remove_hook()` functionality for tracking
        the registered hooks is still at your disposal, but the hooks will simply
        not be executed.

        Returns a handle object that can be used to remove the hook (i.e.
        by using `.remove_hook()`).
        '''

        if when_not_in is None:
            when_not_in = []
        
        if when_in is None:
            when_in = filter(lambda s: not s in when_not_in, self._state_ids)
            
        hook_ref = {}
        for s in when_in:
            pl = self._hooks.setdefault(s, [])
            pl.append(proc)
            hook_ref.setdefault(s, pl[-1])

        return hook_ref


    def _naively_call_hook(self, proc, state, event, enter):
        # Naively calls a hook proc, i.e. assumes it isn't an async
        # fuction. If it is, it is packed on a stack of awaitables
        # and returned as coroutine objects.
        wait_for = []
        result = []
        try:
            p = proc(state, event, enter)
            if inspect.iscoroutine(p):
                wait_for.append(p)
            else:
                result.append(p)
        except Exception as e:
            result.append(e)
            
        return result, wait_for


    def _unwind_results(self, state, result_list):
        # Checks hook return results and returns (new_state, events)
        new_state = None
        events = []

        state_name = lambda x: _state_names[x]
        
        for r in result_list:
            
            if isinstance(r, NewState):
                if new_state is not None:
                    raise RuntimeError(f'msg="Conflicting state change request" '
                                       f'have={state_name(new_state)} '
                                       f'requested={state_name(e.state)}')
                new_state = r.state
                events += r.events
                
            elif isinstance(r, DetectorState):
                if new_state is not None:
                    raise RuntimeError(f'msg="Conflicting state change request" '
                                       f'have={state_name(new_state)} '
                                       f'requested={state_name(e.state)}')
                new_state = r
                
            elif isinstance(r, Exception):
                logger.error(f'state={state_name(state)} msg="Raised exception" error="{r}"')
                #logger.error(traceback.format_exc(r))
                raise r
            
            elif isinstance(r, Iterable):
                events += [e for e in r]
                
            elif isinstance(r, Event):
                events.append(r)
                
            elif r is None:
                pass
            
        return new_state, events


    async def execute(self, state_from, state_to, event):
        # Runs all state hooks. Awaits for coroutine objects.
        # Returns an event list to be injected into the queue,
        # and a new state to switch to (if applicable).
        #
        # Raises an error if any of the hooks raised an exception
        # that isn't explicit state machine flow (i.e. `NewState`)
        
        enter = (state_from != state_to)
        new_state = None
        events = []
        result = []
        awaitables = []

        if not state_to in self._hooks:
            return []
        
        for proc in self._hooks[state_to]:
            res, wait_for = self._naively_call_hook(proc, state_to, event, enter)
            result += res
            awaitables += wait_for

        res = await asyncio.gather(*awaitables, return_exceptions=True)
        result += res

        ns, ev = self._unwind_results(state_to, filter(lambda r: r is not None, result))
        #print(f'New events: {ev}')
        #print(f'New state: {ns}')
        return ns, ev


class ControllerEngine:
    '''
    This one is the entity responsible for clean run-through the
    necessary protocol steps of controlling a detector. Essentially,
    these are:

      - starting up and making sure that first-time initialization
        has been taken care of, or is triggered if it hasn't
        (states INIT, respectively WARMUP)

      - waiting for a new acquisition command (state READY)

      - performing the acquisition / waiting for detector to start
        delivering images (state ACQUIRE)

      - handling the image data after it has been acquired
        (state PROCESS)

      - performing additional tasks like cancelling current
        acquisition, handling errors etc (states CANCEL, ERROR, FAIL)

    The main point of revolution of the state machine is an event
    queue, which processes specific types of events. There are
    two main types:
    
      - Queries (from `QueryEvent`), which are read-only probes
        of the underlying hardware. These never trigger any state
        change of the hardware, but may be in result to state changes
        already occuring within the hardware for various reasons.

      - Requests (from `RequestEvent`), which trigger, induce or control
        specific actions within the hardware. As such, they are by definition
        state-changing events with respect to the underlying hardware.

    Both Queries and Requests usually generate answers (generically just
    called "events"). Some events are specific to a certain request or query,
    others may also arrive at any time, others in turn are generated during
    specific phases of the hardware activity:

      - `CommandResultState` is an event generated as a response to any
        `Command`-type event sent to the hardware backend. It usually
        indicates success or failure (note that success means success of
        transfer, not necessarily that the hardware actually performed
        what was expected). In addition, commands usually trigger actions
        which result in even more events being transmitted -- these usually
        arrive after the corresponding command state event, but not
        necessarily.

      - `ErrorEvent` may arrive at any time and indicates an unexpected
        issue on the backend side. These are usually recoverable errors,
        but require user intervention. They therefore force the state
        machine into an ERROR state (usually not FAIL), resulting in
        cancellation of the running acquisition (if any), and require
        user acknowledgement.

      - Further state events that inform about the current state of the
        hardware (`InitStateEvent`, `ConfigStateEvent`, `RuntimeStateEvent`,
        `ChannelStateEvent`)
    
      - Data events (`StartDataEvent`, `ImageDataEvent`, `EndDataEvent`,
        `CancelDataEvent`) are generated while image acquisition is in
        progress, delivering data, or was cancelled (and no more data
        is to be expected.

    The class has various callback systems that can be used to interact
    with it:
    
      - state hooks: procedures of the signature `proc(state, event, enter)`
        that are executed on every state loop-run. These are the preferred
        mechanism to keep track the state machine work, and keep up with
        its evolution (they are also used internally quite intensively).

      - data hooks: procedures of the signature `proc(data_dict)`, executed
        when a full set of new data (i.e. the result of one acquisition)
        is ready for processing. This is how higher layers receive the data.

      - specific configuration / runtime update hooks, called when new
        information about the hardware state is available (most notably
        channel-meta hooks, called when channel meta-data has changed).
        These usually don't influence the behavior of the system, but are
        nice to have for a more comprehensive display / logging / UI
        system.
    '''
    
    _valid_states = _valid_states
    _state_names = _state_names

    # Quick'n dirty way to access parameters (e.g. from a dict)
    # directly, no strings. This is used to store abstract detector
    # data locally.
    class Config:
        def __repr__(self):
            return \
                f'{self.__class__.__name__}(' + \
                ' '.join([f'{k}="{v}"' for k,v in self.__dict__.items()]) + \
                f')'


    def __init__(self, queue, name=None, period=0.01):
        '''
        Initializes the main Detector Controller state engine.
        
        Args:
            queue: an `EventQueue` instance, the central point
              of the controller <-> device communication.
              This needs to be shared with a `DeviceEngine`
              instance, i.e. your typical hardware "driver".

            name: a string by which this controller is known
              (mostly used for nicer logging)

            period: period with which the `.run()` procedure
              goes through the event loop. Events are being processed
              as fast as they come, but with the following
              restrictions:
                - only one event is processed per loop run
                - there is a minimal `period` waiting time per
                  loop run
              Default is 10 ms, which is plenty for "macroscopic"
              imaging times (i.e. seconds, or large fractions of
              seconds).
        '''

        ## FIXME: too many responsibilities, need to split this up a bit.
        
        self.name = name if name is not None else "ControllerEngine"

        self._events = queue
        self._period = period
        
        self._state = DetectorState.INIT
        self._prev_state = None
        self._state_enter_ts = time.time()

        self._events = queue or EventQueue()
        self._state_hooks = StateHooks(DetectorState)
        self._channel_meta_hooks = {}
        
        self._collector = FrameCollector()
        self._collector_task = None

        self._config = self.Config()        

        # These are errors that are only available locally, i.e. in _this_ object instance.
        # There may be other errors, too (e.g. from device config data)
        self._local_errors = []

        # We have a two-tiered configuration/status reporting system
        # (courtesy of the Eiger detector -- we've decided to implement
        # this natively in the state machine):
        #
        #  - initial phase, when the detector has barely been turned on
        #    and not yet operational, and requires a dedicated (possibly
        #    lengthy) config command
        #   
        #  - operational phase, when the detector is "ready to go"
        #
        # Each of the tiers reports only specific config items; specifically
        # the "init phase" only reports whether the device is initialized or not
        # (and possibly some API versions).
        #
        # This is where we discriminate between the two.
        # This relies on the numerical value of the states themselves!
        self._initial_states = [s for s in \
                                filter(lambda s: s < DetectorState.READY,
                                       self._valid_states)]

        # We automatically check some common error states (mostly communication
        # replies) and enter corresponding states. This is more of a "it's
        # typically like this" than "this is systematic" thing, so if it turns
        # out to be wrong, we need to change this logic.
        # Anyway, the checking needs to happen before anything else, because
        # state-changes here must not be overwritten elsewhere.
        self.add_state_hook(partial(self._check_error_hook, goto=DetectorState.FAIL),
                             when_in=self._initial_states)
        self.add_state_hook(partial(self._check_error_hook, goto=DetectorState.ERROR),
                             when_not_in=self._initial_states)

        # Register all the state-proc as hooks (Init, Ready, ... for states INIT, READY, ...)
        for sval,sname in self._state_names.items():
            hook_name = sname.upper()[0] + sname.lower()[1:]
            self.add_state_hook(getattr(self, hook_name), when_in=[sval])
        
        self.add_state_hook(self._update_config_hook)
        self.add_state_hook(self._query_init_hook, when_in=self._initial_states)
        self.add_state_hook(self._query_runtime_hook, when_not_in=\
                             self._initial_states+[DetectorState.FAIL])


    async def _check_error_hook(self, state, e, enter, goto=None):
        # Checks for incoming error states, exits into ERROR
        #  - device errors (reported via config)
        #  - communication errors (reported via events)
        if isinstance(e, CommandResultState) and \
           (e.state == CommandResult.Failed):
            estr = f'event={e} command="{_Command_i2n[e.command]}" msg="Failed"'
            logger.error(estr)
            self.push_error(e.detail)
            return NewState(goto)
            
        elif isinstance(e, ErrorEvent):
            self.push_error(e)
            if not e.fail:
                return NewState(goto)
            else:
                return NewState(DetectorState.FAIL)

        return None


    @property
    def state_age(self):
        return time.time()-self._state_enter_ts


    def push_event(self, event):
        self._events.push(event)


    def push_error(self, err):
        self._local_errors.append(err)


    def push_query(self, query):
        self._events.push(QueryRequest(query))


    def push_command(self, command, **params):
        self._events.push(CommandRequest(command, **params))        


    def add_state_hook(self, *args, **kw):
        # proc(state, event, enter) to be called on every loop when in `state`
        self._state_hooks.add_hook(*args, **kw)


    def add_data_hook(self, label, proc):
        # proc(data) to be called when new image data available
        self._collector.add_callback(label, proc)


    def add_channel_meta_hook(self, label, proc):
        # proc(channel_name, meta_dict) to be called when channel metadata changes
        self._channel_meta_hooks[label] = proc


    @property
    def collector(self):
        return self._collector


    def errors(self):
        return self._local_errors + \
            (self._config.errors if hasattr(self._config, "errors") else [])


    def clear(self):
        self._local_errors.clear()
        self.push_command(Command.Clear)


    @property
    def config(self):
        return self._config
    

    async def _query_runtime_hook(self, state, event, enter):
        if event is None:
            return QueryRequest(Query.GetRuntime)

    async def _query_init_hook(self, state, event, enter):
        if event is None:
            if not hasattr(self._config, "initialized") or \
               not self._config.initialized:
                return QueryRequest(Query.IsInitialized)
            else:
                #if not hasattr(self._config, "op_mode"):
                return QueryRequest(Query.GetConfig)


    async def _update_config_hook(self, state, event, enter):
        def _update(target, source):
            target.__dict__.update({
                k:getattr(source, k) \
                for k in filter(lambda x: not x.startswith('_'), source.__dir__())
            })

        try:
            if isinstance(event, InitStateEvent):
                if event.initialized:
                    logger.info(f'msg="Detector initialized"')
                _update(self._config, event)
                self._config.configured = False
                logger.debug(self._config)
            elif isinstance(event, ConfigStateEvent):
                logger.info(f'msg="Received detector config update"')
                self._config.configured = True
                _update(self._config, event.config)
            elif isinstance(event, ChannelStateEvent):
                if hasattr(self._config, "channels"):
                    logger.info(f'msg="Received channel state update" channel="{event.channel}" '+
                                ' '.join([f'{k}={v}' for k,v in event.meta.items()]))
                    chobj = next(iter(filter(lambda c: c.label == event.channel,
                                             self._config.channels)))
                    chobj.meta.update(event.meta)
                    wlist = [ p(chobj.label, chobj.meta) for p in self._channel_meta_hooks.values() ]
                    await asyncio.gather(*wlist, return_exceptions=False)
                else:
                    logger.info(f'msg="Received channel state but no base config" channel="{event.channel}"')
            elif isinstance(event, RuntimeStateEvent):
                _update(self._config, event.runtime)
        except Exception as e:
            logger.error(f'msg="Error during config update" detail={e}')
            raise


    def acquire(self, duration):
        '''
        Starts a new image acquisition with integration time `duration` seconds.
        How the image is acquired is a matter for the backend, and is typically
        also dependent on the device operation mode.
        '''
        if not self.state in (DetectorState.READY,):
            logger.error(f'state="{self._state_name}" msg="Cannot acquire in current state"')
            return
        
        self.push_command(Command.Acquire, duration=duration)


    def cancel(self):
        self.push_command(Command.Cancel)


    def set_channel_meta(self, channel, key, val):
        self.push_event(ChannelAdjustCommandRequest(channel, **{key: val}))


    def _successful_command(self, e, cmd):
        return isinstance(e, CommandResultState) and \
           (e.state == CommandResult.Success) and \
           (e.command == cmd)


    def Init(self, state, event, enter):
        if isinstance(event, InitStateEvent):
            if event.initialized:
                return DetectorState.READY
            else:
                return DetectorState.WARMUP

        if event is not None:
            logger.warning(f'state={self.state_name} event="{event}"'
                           f' msg="Ignoring unexpected event"')


    def Warmup(self, state, event, enter):
        if enter:
            return NewState(state, CommandRequest(Command.Initialize))

        if self._config.configured:
            return DetectorState.READY
            

    def Ready(self, state, e, enter):
        if isinstance(e, StartDataEvent):
            self._collector.start(self._config.image_size,
                                  self._config.num_images,
                                  [c.label for c in self._config.channels],
                                  e)
            return NewState(DetectorState.INTEGRATE)
        return self._accept_only(e, StateEvent, type(None))

            
    def Cancel(self, state, event, enter):
        if enter:
            self._collector.reset()
        else:
            return NewState(DetectorState.READY)


    def Integrate(self, state, e, enter):
        if isinstance(e, EndDataEvent):
            return NewState(DetectorState.PROCESS) # cancelled?
        
        elif isinstance(e, CancelDataEvent):
            return NewState(DetectorState.CANCEL)
        
        elif isinstance(e, ImageDataEvent):
            try:
                self._collector.add_image(e)
                return                
            except Exception as e:
                logger.error(f'msg="Error registering image in set, details follow"')
                logger.error(e)
                self.push_error(e)
                return NewState(DetectorState.ERROR)
        
        elif isinstance(e, StartDataEvent):
            self.push_error(f'state={self.state_name} event={e} '
                            f'msg="Unexpected start of data"')
            return NewState(DetectorState.ERROR)

        return self._accept_only(e, StateEvent, type(None))        

            
    def Process(self, state, event, enter):
        if enter:
            assert self._collector_task is None
            self._collector_task = asyncio.create_task(self._collector.callback())
        elif self._collector_task.done():
            r = self._collector_task.result()
            self._collector_task = None
            self._collector.reset()
            return NewState(DetectorState.READY)


    def Error(self, state, event, enter):
        if enter:
            for e in self.errors():
                logger.error(f'state={self.state_name} msg="Detail follows"')
                logger.error(e)
                try:
                    if isinstance(e, Exception):
                        logger.error(traceback.format_exc(e))
                except TypeError as e:
                    logger.info(f'msg="Cannot format traceback" detail="{e}"')
            logger.error(f'state={self.state_name} msg="Waiting for user ack"')
            return

        if len(self._local_errors) > 0:
            return

        self._collector.reset()
        return NewState(DetectorState.READY)


    def Fail(self, state, event, enter):
        if enter:
            for e in self.errors():
                logger.error(str(e))
            logger.error(f'state={self.state_name}')


    def _accept_only(self, e, *types):
        for t in types:
            if isinstance(e, t):
                return

        logger.error(f'state={self.state_name} name={self.name} '
                     f'event="{e}" msg="Unexpected state"')

        return NewState(DetectorState.ERROR)        
    


    async def startup(self):
        self._task = asyncio.create_task(self.run(), name=self.name)

    async def shutdown(self):
        try:
            self._task.cancel()
            await self._task
        except asyncio.CancelledError:
            pass

    async def __aenter__(self, *args, **kw):
        await self.startup()
        return self


    async def __aexit__(self, *args, **kw):
        await self.shutdown()
        

    @property
    def state_name(self):
        return self._state_names[self._state]
    

    def _state_proc(self, state, enter):
        '''
        Returns a callable to handle the current state, or `None` if there
        is no callable defined. `enter` demarks whether this is a switch
        from another state (`True`), or this is just another run of the
        same state (`False`).

        The state procedures are designated by name, `state_<NAME>`,
        respectively `enter_<NAME>`.
        '''
        sname = self.state_name
        if not enter:
            return getattr(self, f"state_{sname}") \
                if hasattr(self, f"state_{sname}") \
                   else print(f'State: {sname}, no proc')
        else:
            return  getattr(self, f"enter_{sname}") \
                if hasattr(self, f"enter_{sname}") \
                   else self._state_proc(state, False)

    
    async def _state_step(self):
        '''
        Executes one single state step. Essentially, call the current
        state proc, save the new state, call state hooks.
        '''

        try:
            enter = (self._prev_state != self._state)
            event = self._events.pop_role(DetectorEngineRole.CONTROLLER,
                                          raise_empty=False)
            
            new_state, events = await self._state_hooks.execute(self._prev_state,
                                                                self._state, event)
            if new_state is None:
                new_state = self._state

            self._prev_state = self._state
            self._state = new_state

            if self._state not in (self._prev_state, None):
                self._state_enter_ts = time.time()
                if self._prev_state is not None:
                    logger.info(f'msg="State switch" '
                                f'old={self._state_names[self._prev_state]} '
                                f'new={self._state_names[new_state]}')
                assert new_state in self._valid_states

            self._events.push(events)

        except Exception as e:
            logger.error(f'state={self._state_names[self._state]} enter={enter} '
                         f'msg="Error in state proc" error="{str(e)}"')
            logger.error(traceback.print_exc())
            self._prev_state = self._state
            self._state = DetectorState.FAIL


    async def step(self):
        await self._state_step()


    @property
    def state(self):
        return self._state


    async def run(self, period=None, stop_on_fail=True, raise_on_fail=False):
        
        if period is None:
            period = self._period

            
        while (self._state not in { DetectorState.FAIL }) or (not stop_on_fail):
            try:
                await asyncio.gather(self.step(), asyncio.sleep(period),
                                     return_exceptions=False)
            except Exception as e:
                logger.error(f'Detector engine failed: {str(e)}')
                logger.error(traceback.format_exc())
                self._state = DetectorState.FAIL
                if raise_on_fail:
                    raise
