from diss_ioc.controller import (
    # General command/query stuff
    CommandRequest, Command, CommandResult, CommandResultState,
    QueryRequest, Query, ErrorEvent, 

    # State management and workflow
    NewState, DetectorState, DetectorEngineRole,

    # Configuration and status reporting
    DeviceConfig, ChannelConfig, DeviceState, DeviceRuntime,
    InitStateEvent, ConfigStateEvent, RuntimeStateEvent, ChannelStateEvent,

    # Image transfer stuff
    StartDataEvent, EndDataEvent, ImageDataEvent, CancelDataEvent,
)

from diss_ioc.devices.base import (
    DeviceEngineBase,
    command_handler, query_handler,
)


import pprint, inspect, random, string, time, asyncio, logging

from numpy.random import rand as arand
from diss_ioc.event import *
from diss_ioc.devices.base import *

logger = logging.getLogger(__name__)

class DeviceEngine(DeviceEngineBase):

    def __init__(self, *a, sim_dict=None, **kw):
        '''
        Accepted sim_params:
          - warmup: time to wait before reporting init=True
        '''

        super().__init__(*a, **kw)
        self._is_initialized = False
        self._config = None
        self._sim_params = sim_dict if sim_dict is not None else {}
        self._series_counter = -1
        self._cancel_acquisition = False


    async def startup(self, *a, **kw):
        pass


    async def teardown(self):
        pass


    @property
    def _num_images(self):
        return self._config.num_images


    def _make_random_channel(self):
        return ChannelConfig(''.join(random.choices(string.ascii_lowercase, k=4)),
                             meta_dict={'enerj': 3.14})


    def _make_random_config(self):
        s = DeviceConfig()
        for c in range(0, random.randint(a=1, b=4)):
            ch = self._make_random_channel()
            s.channels.append(ch)
        s.num_images = self._sim_params.get('num_images', random.randint(1, 7))
        s.image_size = [ random.randint(128, 256), random.randint(128, 256) ]
        s.pixel_size = [ random.random() * 1e-4, random.random() * 1e-4 ]
        logger.info(f'device={__name__} num_images={s.num_images} '
                    f'image_size={s.image_size[0]}x{s.image_size[1]} '
                    f'pixel_size={s.pixel_size[0]}x{s.pixel_size[1]} '
                    f'channels="{[c.label for c in s.channels]}"')
        return s    


    @command_task(Command.Initialize)
    async def _run_initialize(self, cmd):
        t0 = time.time()
        await asyncio.sleep(self._sim_params.get('warmup', 5.0))
        self._config = self._make_random_config()
        self._is_initialized = True


    @command_task(Command.Acquire)
    async def _run_acquire(self, cmd, duration=None):
        logger.info(f'msg="Sim acquire start"')

        class _Canceled(Exception): pass

        async def _integrate_for_duration(d):
            t0 = time.time()
            while (time.time()-t0) < d:
                await asyncio.sleep(0.001)
                if self._cancel_acquisition:
                    raise _Canceled()
        
        try:
            self._cancel_acquisition = False
            self._series_counter += 1

            data_start = StartDataEvent(self._series_counter,
                                        note="This is a random sim series")
            
            self.push_event(data_start)
            
            for img_id in range(self._num_images):

                tstart = time.time()
                
                await _integrate_for_duration(duration)
                data_image = ImageDataEvent(img_id, series_uuid=data_start.uuid,
                                            start_ts=tstart,
                                            duration=time.time()-tstart)
                
                for channel in self._config.channels:
                    data_image.add_image(channel.label, arand(*self._config.image_size)*256)

                self.push_event(data_image)
                
            self.push_event(EndDataEvent(series_uuid=data_start.uuid))

        except _Canceled as e:
            self.push_event(CancelDataEvent(series_uuid=data_start.uuid))
            
        except Exception as e:
            self.push_event(ErrorEvent(str(e)))

        logger.info(f'msg="Sim acquire done"')


    @command_task(Command.ChannelAdjust)
    async def _run_channel_adjust(self, channel_name=None, **params):
        # We run this in a separate task to simulate a time delay
        # between the command and the actual data having been sent
        # to the detector.

        try:
            await asyncio.sleep(0.5)

            if channel_name not in [c.label for c in self._config.channels ]:
                self.push_event(ErrorEvent(f'msg="No such channel trying to set meta" '
                                           f'channel="{channel_name}"'))

            chobj = next(iter(filter(lambda x: x.label == channel_name, self._config.channels)))
            chobj.meta.update(params)

            await asyncio.sleep(0.5)

            self.push_event(ChannelStateEvent(channel_name, **(chobj.meta)))

        except Exception as e:
            logger.error(f'msg="Error updating channel meta, detail follows" channel="{channel_name}"')
            logger.error(str(e))
            self.push_event(ErrorEvent(str(e)))
            try:
                logger.error(traceback.format_exc(e))
            except:
                logger.error('msg="Cannot print traceback"')


    @command_task(Command.Cancel)
    async def _run_cancel(self, cmd):
        self._cancel_acquisition = True


    @command_task(Command.Clear)
    async def _run_clear(self, cmd):
        logger.info(f'msg="Nothing to do on h/w driver level."')


    @query_handler(
        Query.GetConfig,
        Query.GetRuntime,
        Query.IsInitialized
    )
    def _queries(self, event):
        return {
            Query.IsInitialized: InitStateEvent(self._is_initialized),
            Query.GetRuntime: RuntimeStateEvent(DeviceRuntime()),         
            Query.GetConfig: ConfigStateEvent(self._config) \
                if self._config is not None \
                else ErrorEvent(f'Device not initialized')
        }[event.query]
