#!/usr/bin/python3

from diss_ioc.device import Detector as Detector
import asyncio, time, inspect, concurrent, sys, logging, importlib
import diss_ioc.event as det
from diss_ioc.controller import ControllerEngine

logger = logging.getLogger(__name__)

from diss_ioc._version import version

class EigerApplication:
    '''
    Base class for Eiger-IOC-like applications.

    Mostly does (user-side) configuration, logging preparation,
    initialization of various Device backends, acquisition
    loop etc. The idea is to subclass this in order to build
    various trigger-acquire-process-repeat-style applications,
    which is essentially everything from simple Matplotlib live
    viewers, to the EPICS IOC itself.
    '''
    
    def __init__(self, args, env, sink=None, stat=None):
        '''
        Initializes the application.

        Args:
            args: Command line arguments. Mostly ignored (for now),
              but here for future use. Probably

            env: Env-vars dictionary. This is the main configuration
              source for the application and, if missing, it's
              extracted from `os.environ`. If you truly want to start
              the application with an empty configuration (i.e. only
              using defaults), pass an empty `dict()` here.

            sink: Callable to process one set of incoming data. Call
              signature is `proc(data)`, where `data` is a dictionary
              with field names as keys, and the actual data (typically
              numbers, string items, numpy arrays) as values.
              This is called every time a data point is received.
              It doesn't need to be a coroutine, but if it is, it
              is awaited.

            stat: Callable to process incoming runtime state updates.
              This is a callable with an `diss_ioc.detector.DeviceConfig`
              namespace as its argument `await proc(config)`, called
              typically once per detector engine loop.
        '''

        self._args = args
        self._env = env if env is not None else os.environ.copy()
        self._device_spec = None
        self._sink = sink
        self._stat = stat

        logger.info(f'name={self.__class__.__name__} version={version}')


    def set_data_sink(self, proc):
        self._sink = proc


    def _parse_device_module(self, spec):

        if spec is None:
            spec = self._env.get('DISS_DEVICE_BACKEND', '')

        s = spec.split(':')
        
        if len(s) == 2:
            return s
        elif len(s)==1 and len(s[0]) > 0:
            return (f"diss_ioc.devices.{s[0]}", "DeviceEngine")
        else:
            raise RuntimeError(f'msg="Funny device spec" device="{spec}"')


    def _get_device_class(self, mod_name, cls_name):
        try:
            mod_obj = importlib.import_module(mod_name)
            #logger.info(f'modobj="{mod_obj}"')
            cls_obj = getattr(mod_obj, cls_name)
            #logger.info(f'clsobj="{cls_obj}"')
            return cls_obj
        
        except Exception as e:
            logger.error(f'msg="Cannot load detector device" detail="{e}" '
                         f'module="{mod_name}" class="{cls_name}"')
            raise


    def _inject_acquire(self, state, event, enter):
        if (state == det.DetectorState.READY) and (self._auto_acquire != False):
            if enter:
                self._last_acquire = time.time()
                logger.info(f'msg="Auto-acquire is activated with fixed duration" '
                            f'duration="{self._auto_acquire}"')
                return det.AcquireCommandRequest(duration=self._auto_acquire)

    
    async def init_detector(self):
        self._queue = det.EventQueue()
        mod_name, cls_name = self._parse_device_module(self._device_spec)
        DeviceEngine = self._get_device_class(mod_name, cls_name)
        logger.info(f'object="{DeviceEngine}" module="{mod_name}" class="{cls_name}"')

        try:
            acq = self._env.get('DISS_AUTO_ACQUIRE', 'no').lower()
            self._auto_acquire = float(acq) if acq \
                not in ('no', 'nope', 'false', '0') else False
        except ValueError:
            self._auto_acquire = 1.0
            
        logger.info(f'msg="Auto-acquire {self._auto_acquire}"')
        
        self._ctl = ControllerEngine(self._queue)
        self._ctl.add_state_hook(self._inject_acquire, when_in=[det.DetectorState.READY])

        self._dev = DeviceEngine(self._queue, args=self._args, env=self._env)
        await self._dev.startup()

        self._ctl.add_data_hook("ioc", self._data_incoming)


    async def _data_incoming(self, data):
        if self._sink is not None:
            if inspect.iscoroutinefunction(self._sink):
                return await self._sink(data)
            else:
                return self._sink(data)


    async def _status_incoming(self):
        try:
            if self._stat is not None:
                if inspect.iscoroutinefunction(self._stat):
                    return await self._stat(self._ctl)
                else:
                    return self._stat(self._ctl)
        except Exception as e:
            logger.error(f'msg="{e}"')
            raise


    async def run_init(self):
        return await self.init_detector()


    async def run_step(self):
        return await asyncio.gather(self._dev.step(),
                                    self._ctl.step(),
                                    self._status_incoming(),
                                    return_exceptions=True)

    async def run(self, period=0.01):
        await self.run_init()
        while True:
            try:
                await asyncio.gather(asyncio.sleep(period),
                                     self.run_step(),
                                     return_exceptions=True)

                if self._ctl.state == det.DetectorState.FAIL:
                    logger.error(f'msg="Better luck next time"')
                    break

            except Exception as e:
                logger.error(f'msg="Bailing out" error={e}')
                logger.error(traceback.format_exc(e))
                await self._dev.teardown()
                break

