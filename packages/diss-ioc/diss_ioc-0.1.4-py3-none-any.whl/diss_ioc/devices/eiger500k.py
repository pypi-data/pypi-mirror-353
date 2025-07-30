#!/usr/bin/python3

from diss_ioc.event import *
from diss_ioc.event import _detector_op_mode_names

from diss_ioc.devices.base import *

from diss_ioc.image import image_unpack

from contextlib import suppress

import pprint, inspect, random, string, time, asyncio, logging, enum, \
    aiohttp, yaml, zmq, cbor2, datetime, json, os, parse


logger = logging.getLogger(__name__)

### The communication with Eiger has an event structure of its own.
### These are mostly easily translatable (1:1) to the abstract
### Detector events.


class EigerOpMode(enum.IntEnum):
    # Operational modes: note that every image mode can deliver
    # multiple images (i.e. for multiple enery thresholds),
    # but the SINGLE/DOUBLE modes are expected to generate 1,
    # respectively 2 images on every trigger pulse.
    SNAPSHOT = 0   # (single) image type upon user request 
    SINGLE = 1  # single image type upon external trigger
    DOUBLE = 2  # double-image type upon external trigger

_detector_op_mode_names = {
    v:k for k,v in filter(lambda x: not x[0].startswith('_'),
                          EigerOpMode.__dict__.items())
}

class EigerApiSubsystem(enum.StrEnum):
    ''' Eiger API subsystems (there may be others we're not using here) '''
    DETECTOR = "detector"
    MONITOR = "monitor"
    SYSTEM = "system"
    STREAM = "stream"


class EigerApiGroup(enum.StrEnum):
    ''' Eiger API-call groups (not every group is available in every subsystem) '''
    CONFIG = "config"
    STATUS = "status"
    COMMAND = "command"
    STREAM = "stream"
    

class EigerRequest:
    '''
    Base class for all HTTP API requests we send to the Eiger.

    Generally, the Eiger HTTP API is REST-ish, with URLs of the form:
    
      ` http://{host}/{subsystem}/api/{api_version}/{group}/{detail} `

    Sometimes there are extra parameters that can be passed in a JSON
    package. There's a difference between "commands" (HTTP verb "POST",
    changing state, usually the only ones that also may have parameters)
    and "queries" (HTTP verb "GET", no state change).
    '''

    subsystem = None
    group = None
    detail = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.detail})'


class EigerCommandRequest(EigerRequest):
    ''' Built by App, transmitted to Eiger (usually by HTTP "PUT") '''
    subsystem = EigerApiSubsystem.DETECTOR
    group     = EigerApiGroup.COMMAND


class ArmRequest(EigerCommandRequest):
    detail = 'arm'

class DisarmRequest(EigerCommandRequest):
    detail = 'disarm'

class AbortRequest(EigerCommandRequest):
    detail = 'abort'

class CancelRequest(EigerCommandRequest):
    detail = 'cancel'
        
class TriggerRequest(EigerCommandRequest):
    detail = 'trigger'


class EigerConfigRequest(EigerRequest):
    def __init__(self, detail=None, value=None, subsystem=None, group=None):
        assert detail is not None
        assert value is not None
        self.detail = detail
        self.value = value
        if subsystem is not None:
            self.subsystem = subsystem
        if group is not None:
            self.group = group


class CountTimeRequest(EigerConfigRequest):
    '''
    Simple wrapper to request a count-time change.

    For internal trigger modes, `sec` is enough. For external triggers,
    count time is expressed as a number of gating cycles, so count
    time is expressed as a function of the gating frequency.
    
    '''
    def __init__(self, sec, mode=None, gfreq=None):
        if mode in (None, DetectorOpMode.SNAPSHOT):
            super().__init__('count_time', float(sec),
                             subsystem='detector',
                             group='config')
        elif mode in (DetectorOpMode.SINGLE, DetectorOpMode.DOUBLE):
            if gfreq is None:
                raise RuntimeError(f'BUG -- need a gating frequency for '
                                   f'external trigger count time setup')
            cycles = int(sec * gfreq / (1+int(mode==DetectorOpMode.DOUBLE)))
            logger.info(f'msg="Acquisition by cycles" repetion={gfreq} cycles={cycles}')
            super().__init__('nexpi', cycles,
                             subsystem='detector',
                             group='config')


class DetectorConfigRequest(EigerConfigRequest):
    subsystem = EigerApiSubsystem.DETECTOR
    group     = EigerApiGroup.CONFIG


class EigerQueryRequest(EigerRequest):
    '''
    Queries the system (i.e. no API change, HTTP verb "GET".
    This specialization is only to add a 'detail' parameter
    in __init__() for easier building of requests.
    '''
    def __init__(self, detail):
        self.detail = detail

class DetectorConfigQuery(EigerQueryRequest):
    subsystem = EigerApiSubsystem.DETECTOR
    group     = EigerApiGroup.CONFIG

class DetectorStatusQuery(EigerQueryRequest):
    subsystem = EigerApiSubsystem.DETECTOR
    group     = EigerApiGroup.STATUS

class StreamConfigQuery(EigerQueryRequest):
    subsystem = EigerApiSubsystem.STREAM
    group     = EigerApiGroup.CONFIG

##
## These are all the queries ("runtime info") we're going to
## repeatedly perform on the Eiger. The format of the map
## is '{subsystem}.{group}.{detail}' -> QueryObject(...)
##
_eiger_query_map = {}
for QueryType,fields in {
    DetectorConfigQuery:
        [ 'auto_sum_strict',      'auto_summation',
          # cannot be set in gated mode?
          ## 'binning_mode',      'pixel_format',
          # 'flatfield',          'pixel_mask',                                   
          'bit_depth_image',      'bit_depth_readout',
          'compression',          'count_time',         'counting_mode',
          'eiger_fw_version',     'extg_mode',
          'frame_time',           'nexpi',              'nimages', 'ntrigger',
          'pixel_mask_applied',   'photon_energy',      'test_image_mode',
          'threshold/1/energy',   'threshold/2/energy',
          'trigger_mode',         'trigger_start_delay',
          'x_pixel_size',         'y_pixel_size',
          'x_pixels_in_detector', 'y_pixels_in_detector',
          'countrate_correction_applied',
          'flatfield_correction_applied',
          'detector_readout_time'
         ],
    DetectorStatusQuery: [
        'state', 'temperature', 'humidity', 'time'
    ],
    StreamConfigQuery: [
        'format', 'header_detail', 'mode'
    ],}.items():
    _eiger_query_map.update({
        f'{QueryType.subsystem}.{QueryType.group}.{detail}':QueryType(detail) \
        for detail in fields
    })


##
## We have 3 distinct opmodes: SNAPSHOT, SINGLE, DOUBLE.
## In the end, we want to end up with '_eiger_opmode_settings'
## as a dictionary which has each of the opmodes as keys,
## and a corresponding settings dictionary as values.
## The settings dictionaries themselves have ('{subsystem}', '{group}', '{detail}')
## tuples as keys, and the desired values as values.
## Since many options repeat, we're doing some trickery
## to make a quasi-hierarchical setup.
##

# valid settings for all modes
_eiger_general_settings = {
    ('detector', 'config', 'test_image_mode'): '',
    ('detector', 'config', 'countrate_correction_applied'): False,
    ('detector', 'config', 'pixel_mask_applied'): False,
    ('detector', 'config', 'auto_summation'): False,
    ('detector', 'config', 'counting_mode'): "normal",
    ('detector', 'config', 'threshold/1/energy'): \
    float(os.environ.get("EIGER_X2_THRESHOLD1_ENERGY", "7000")),
    ('stream', 'config', 'format'): 'cbor',
    ('stream', 'config', 'mode'): 'enabled'
}

_th2e = os.environ.get("EIGER_X2_THRESHOLD2_ENERGY", None)
if _th2e is not None:
    _eiger_general_settings.update({
        ('detector', 'config', 'threshold/2/energy'): float(_th2e)
        ('detector', 'config', 'threshold/2/mode'): True,
    })

# additional settings for internally-triggered modes (SNAPSHO)
_eiger_ints_settings = {
    ('detector', 'config', 'trigger_mode'): 'ints',
    ('detector', 'config', 'countrate_correction_applied'): True,    
}

# additional settings for all externally triggered modes (SINGLE, DOUBLE)
_eiger_extg_settings = {
    ('detector', 'config', 'ntrigger'): 1,    
    ('detector', 'config', 'trigger_mode'): "extg",
}

_eiger_opmode_settings = {
    DetectorOpMode.SNAPSHOT: {
        **_eiger_general_settings,
        **_eiger_ints_settings,
        **{
            ('detector', 'config', 'nimages'): 1,
        }
    },
     
    DetectorOpMode.SINGLE: {
        **{
            ('detector', 'config', 'extg_mode'): "single",
            ('detector', 'config', 'nimages'): 1,
        },
        **_eiger_general_settings,
        **_eiger_extg_settings
    },
    
    DetectorOpMode.DOUBLE: {
        **{
            ('detector', 'config', 'nimages'): 2,            
            ('detector', 'config', 'extg_mode'): "double",
        },
        **_eiger_general_settings,
        **_eiger_extg_settings,
    }
}


class Eiger2XApiConnector:
    '''
    Handles HTTP-API communication with an Eiger2X device
    '''
    def __init__(self, host, port=80):
        # don't touch this; it's not that simple.
        self._api_version = "1.8.0"

        self._host = host
        self._port = port

        # This is a dictionary with {subsystem}.{group}.{detail} as keys,
        # and the corresponding value as values, representing the current
        # hardware state. It gets updated in a loop inside .run().
        self.eiger_status = {}

        # Typical format of how channels are named in Eiger.
        # (I think this is hard-coded in the device.)
        self._channel_label_format = 'threshold_{chid:d}'

        # There is a number of settings per-channel ("metadata keys").
        # This maps "our" internal name to "{subsystem}.{group}.{detail}"
        # notation of the corresponding parameter.
        self._channel_meta_format = {
            'threshold_energy': ('detector', 'config', 'threshold/{chid:d}/energy')
        }

        # threshold_1 and threshold_2 are hard-coded in Eiger (?)
        self._channel_ids = (1, 2)


        # Incrementing this counter once per status update is the poor man's
        # way if finding out when there's new information available about
        # the detector hardware.
        self.status_version = 0


    def _make_channel_config(self, chid):
        label = self._make_channel_label(chid)
        
        param_components = {
            mkey:[ p.format(chid=chid) for p in conf ] \
            for mkey,conf in self._channel_meta_format.items()
        }

        # make "{subsystem}.{group}.{detail}" keys to query self.eiger_status
        param_status_keys = {
            mkey:'.'.join(comp) for mkey,comp in param_components.items()
        }

        # Query actual param startup values
        params = {
            mkey:self.eiger_status[skey] for mkey,skey in param_status_keys.items()
        }
        
        return ChannelConfig(label=label, meta_dict=params)


    def _chid_from_label(self, label):
        ret = parse.parse(self._channel_label_format, label)
        return ret['chid']


    def _make_channel_label(self, chid):
        return self._channel_label_format.format(chid=chid)


    async def _request_json(self, hcli, subsystem, ptype, req=None, **req_kw):
        '''
        Helper to transmit a specific query (PUT, ...) to a specific
        subsystem (detector, stream, ...) for a specific subtype (config, ...)
        and check for success.

        Raises RuntimeError if the query is not successful (currently only
        accepting HTTP code 200).

        Returns the AIOHTTP reply as text, but that's mostly moot.
        '''
                
        transform = lambda x: { 'value': x }
        
        req_dict = req if req is not None else {}
        
        req_dict.update({ k:transform(v) for k,v in req_kw.items() })
        q_data = json.dumps(req_dict)        
        q_url = self._make_url(subsystem, ptype)

        try:
            #print('>>>', q_url, q_data)
            async with await hcli.put(q_url, data=q_data) as resp:
                #print(f'(awaiting response for {q_url})')
                resp.raise_for_status()
                r = await resp.text()
                #print('<<<', r)
                return r
        except Exception as e:
            logger.error(f'msg="Query error" error="{e}"')
        finally:
            #print(f'{q_url} cancelled?')
            pass


    def _make_url(self, subsystem, group):
        return f'http://{self._host}:{self._port}/{subsystem}/' \
            f'api/{self._api_version}/{group}'


    async def _exec_queries(self, hcli, qmap):
        ##
        ## We build a giant async query list and asyncio.gather() all of them
        ## before we return.
        ##
        transform=lambda x: x['value'] if hasattr(x, '__getitem__') else x

        async def _fetch(h, q):
            url_fetch = f'{self._make_url(q.subsystem, q.group)}/{q.detail}'
            async with h.get(url_fetch) as response:
                t = await response.text()
                return yaml.safe_load(t)
        
        reply = await asyncio.gather(*[_fetch(hcli, q) for k,q in qmap.items()],
                                     return_exceptions=False)
        
        return { k:transform(r) for k,r in zip(qmap, reply) }


    async def req(self, obj):
        if isinstance(obj, EigerConfigRequest):
            await self._request_json(self._http_client, obj.subsystem, obj.group,
                                     **{f'{obj.detail}': obj.value})
        elif isinstance(obj, EigerCommandRequest):
            await self._request_json(self._http_client, obj.subsystem,
                                     f'{obj.group}/{obj.detail}')
        else:
            raise RuntimeError(f'msg="Unknown query type" query="{obj}"')


    def _publish_channel_config(self, ev_queue):
        # Publishes changes to the channel config (if any)
        if not hasattr(self, "_channel_config"):
            self._channel_config = {}

        for chid in self._channel_ids:
            old_cfg = self._channel_config.get(chid, None)
            new_cfg = self._make_channel_config(chid)            
            if (old_cfg is not None) and (new_cfg != old_cfg):
                    new_data = ' '.join([f'{k}={v}' for k,v in new_cfg.meta.items()])
                    #logger.debug(f'msg="Eiger channel update" channel={new_cfg.label} {new_data}')
                    ev_queue.push(ChannelStateEvent(channel=new_cfg.label, **(new_cfg.meta)))
            self._channel_config[chid] = new_cfg


    async def run(self, ev_queue, period=0.1):
        '''
        Runs a periodic hardware state/status check via HTTP API.
        Not sure what to do with `ev_queue` at this level.
        '''
        http_client = aiohttp.ClientSession(connector=aiohttp.TCPConnector(enable_cleanup_closed=True),
                                            raise_for_status=True)
        logger.info(f'http={http_client}')
        self._http_client = http_client
        while True:
            try:
                self.eiger_status, moo = await asyncio.gather(
                    self._exec_queries(http_client, _eiger_query_map),
                    asyncio.sleep(period),
                    return_exceptions=False
                )

                self._publish_channel_config(ev_queue)

                # Poor man's way of finding out when status updates are available
                self.status_version += 1
                
            except Exception as e:
                logger.error(f'msg="Status query failed" error="{e}"')
                await http_client.close()
                raise

    @property
    def eiger_is_initialized(self):
        return not (self.eiger_status.get('detector.status.state', None) \
                    in (None, "na", "initialize"))

    @property
    def eiger_is_ready(self):
        return (self.eiger_status.get('detector.status.state', None) \
                    in ("ready", "idle"))


    @property
    def eiger_config(self):
        s = DeviceConfig()
        
        emode = self.eiger_status.get('detector.config.trigger_mode', None)
        if emode in ('ints',):
            op_mode = EigerOpMode.SNAPSHOT
            num_images = 1
        elif emode in ('extg',):
            op_mode = {
                'single': EigerOpMode.SINGLE,
                'double': EigerOpMode.DOUBLE
            }[self.eiger_status.get('detector.config.extg_mode', None)]
            num_images = 1 if op_mode == EigerOpMode.SINGLE else 2
        else:
            #raise RuntimeError(f'msg="Unsupported mode" mode="{emode}"')
            logging.error(f'msg="Unsupported mode" mode="{emode}"')
            return None

        logger.info(f'msg="Eiger op-mode" mode="{_detecor_op_mode_names[op_mode]}"')

        # This is (slow data, fast data), i.e. (Height, Width), i.e. (y-size, x-size)
        s.image_size = [ self.eiger_status['detector.config.y_pixels_in_detector'],
                         self.eiger_status['detector.config.x_pixels_in_detector'] ]
        s.pixel_size = [ self.eiger_status['detector.config.y_pixel_size'],
                         self.eiger_status['detector.config.x_pixel_size'] ]

        # We hard-code channels "threshold_1" and "threshold_2".
        s.channels = [ self._make_channel_config(chid=i) for i in self._channel_ids ]
        
        return s


    async def _set_channel_param(self, chid, key, val):
        pass


    @property
    def eiger_runtime(self):
        r = DeviceRuntime()
        r.raw_state = self.eiger_status['detector.status.state']
        r.errors = []
        return r

 
class Eiger2XStreamTimeout(Exception): pass   
    
class Eiger2XZmqConnector:
    '''
    Handles ZMQ Communication with an Eiger2X device
    '''

    def __init__(self, host, port=31001, scheme=None, zmq_sock_type=zmq.PULL):
        self._host = host
        self._port = port
        self._scm = scheme if scheme is not None else "tcp"
        self._zmq_sock_type = zmq_sock_type
        self._image_series_state = {}


    async def wait_for_stream_begin(self, timeout=0.0):
        t0 = time.time()
        while time.time()-t0 < timeout:
            if self._image_series_state.get('uuid', None) is not None:
                return
            await asyncio.sleep(1.0)
        raise Eiger2XStreamTimeout(f'msg="Timeout waiting for image series start"')


    def start_data_event_factory(self, msg):
        event = StartDataEvent(msg['series_id'])
        self._image_series_state.update({
            'uuid': event.uuid,
            'numid': event.numid,
            'eiger_id': msg['series_unique_id'],
        })
        return event


    def _check_series_id(self, numid, eigerid):
        if eigerid != self._image_series_state.get('eiger_id', None) or \
           numid != self._image_series_state.get('numid', None):
            raise RuntimeError(f'msg="Image out of series" '
                               f'expected={self._image_series_state["eiger_id"]} '
                               f'received={eigerid}')


    def image_data_event_factory(self, msg):
        self._check_series_id(msg['series_id'], msg['series_unique_id'])
        start_time = msg['series_date']
        start_time += datetime.timedelta(float(msg['start_time'][0]/msg['start_time'][1]))
        series_uuid = self._image_series_state['uuid']
        image_id = msg['image_id']
        event = ImageDataEvent(imgid=msg['image_id'],
                               series_uuid=series_uuid,
                               start_ts=start_time.timestamp(),
                               duration=msg['real_time'][0]/msg['real_time'][1])
        for iname,ipix in msg['data'].items():
            pixel_data = image_unpack(ipix)
            logger.info(f'msg="Pixel statistics" '
                        f'series={series_uuid} '
                        f'image={image_id} '
                        f'min={pixel_data.min()} '
                        f'max={pixel_data.max()} '
                        f'sum={pixel_data.sum()} '
                        f'shape={pixel_data.shape}')
            event.add_image(iname, pixel_data)

        return event


    def end_data_event_factory(self, msg):
        self._check_series_id(msg['series_id'], msg['series_unique_id'])
        event = EndDataEvent(series_uuid=self._image_series_state['uuid'])
        self._image_series_state.clear()
        return event


    def cancel_data_event_factory(self, msg):
        # This 'msg' is usually belongs to an ImageDataEvent.
        mt = msg['type']        
        if mt != 'image':
            logger.warning(f'msg="CancelDataEvent constructed from unexpected event type {mt}"')
        self._check_series_id(msg['series_id'], msg['series_unique_id'])
        event = CancelDataEvent(series_uuid=self._image_series_state['uuid'])
        self._image_series_state.clear()
        return event


    @property
    def current_uuid(self):
        try:
            return self._image_series_state['uuid']
        except KeyError:
            pass


    def mark_as_cancelled(self):
        # When cancelling an acquisition, apparently the Eiger sends one final
        # ImageDataEvent(). We don't want that, we want a CancelDataEvent()
        # instead to be transmitted to the Collector.
        # Here's where we tell the collector to do the right thing.
        my_uuid = self._image_series_state.get('uuid', None)
        if my_uuid is not None:
            self._image_series_state['cancelled'] = True
        return my_uuid


    async def _query_events(self, ev_queue):
        event_types = {
            "start": StartDataEvent,
            "image": ImageDataEvent,
            "end": EndDataEvent,
        }

        try:        
        
            zpoll = await self._zmq_socket.poll(timeout=0)

            if zpoll != 0:
                t0 = time.time()
                zpack = await self._zmq_socket.recv_multipart()
                for i,buf in enumerate(zpack):
                    msg = cbor2.loads(buf)
                    etype = msg["type"]
                    try:
                        if self._image_series_state.get('cancelled', False) == True:
                            logger.info(f'msg="Ignoring {etype}-type event of cancelled series"')
                            continue
                        event_factory = getattr(self, f'{etype}_data_event_factory')
                        event = event_factory(msg)
                        ev_queue.push(event)
                    except Exception as e:
                        logger.error(f'msg="Cannot build (possibly out-of-order) message" '
                                     f'type="{etype}" reason="{e}"')
        except Exception as e:
            logger.error(f'msg="Error processing ZMQ stream, details follow"')
            logger.error(e)
            raise


    async def run(self, ev_queue, period=0.01, zmq_sock_type=zmq.PULL):
        '''
        Runs a periodic ZMQ message retrieval & dispatch.
        `ev_queue` is a Controller event queue where we put
        StartImageEvent, DataImageEvent etc.
        '''
        try:        
            self._zmq_ctx = zmq.asyncio.Context()
            self._zmq_socket = self._zmq_ctx.socket(zmq_sock_type)
            self._zmq_conn = self._zmq_socket.connect(f'{self._scm}://{self._host}:{self._port}')
            logger.info(f'zmq={self._zmq_conn}')

            while True:
                await asyncio.gather(asyncio.sleep(period),
                                     self._query_events(ev_queue),
                                     return_exceptions=False)
        except Exception as e:
            logger.error(f'msg="ZMQ data stream error" error="{e}"')


class DeviceEngine(DeviceEngineBase):
    '''
    Event handler for communication with hardware for an Eiger 2 X
    (tested on a 500 K model, API version 1.8)
    '''

    def __init__(self, *a, host=None, op_mode=None, gfreq=None, **kw):
        super().__init__(*a, **kw)

        # Operational mode -- one of "snapshot", "single", "double"
        self._target_op_mode = op_mode if op_mode is not None else \
            {
                'snapshot': EigerOpMode.SNAPSHOT,
                'single': EogerOpMode.SINGLE,
                'double': EigerOpMode.DOUBLE
            }[self._env.get('EIGER_DEVICE_MODE', 'snapshot').lower()]

        # Initialization of the "thing" (i.e. everything -- hardware, settings,
        # application) is a complex beast. On one hand we want to just take over
        # the current state, in particular with regars to Eiger initialization.
        # On the other hand we need to do particular settings for the particular
        # op-mode we want to use (setting various config parameters of Eiger).
        # Only then do we regard the "device" as initialized.
        #
        # This variable is intended to signalize exactly that.
        self._setup_finished = False

        # This is the frequency of the external gating pulse, in Hz
        self.gating_frequency = gfreq if gfreq is not None else \
            float(self._env.get('EIGER_GATING_FREQUENCY', "104500.0"))

        # Where to connect to Eiger to -- this is the same for
        # both API and ZMQ streams.
        if host is None:
            host = self._env.get('EIGER_DEVICE_HOST', 'eiger.example.com')

        api_port = int(self._env.get('EIGER_API_PORT', '80'))
        zmq_port = int(self._env.get('EIGER_STREAM_PORT', '31001'))
            
        self._api_con = Eiger2XApiConnector(host=host, port=api_port)
        self._zmq_con = Eiger2XZmqConnector(host=host, port=zmq_port)

        # Timeout for delivering the first image after a ACQUIRE command.
        # For SNAPSHOT mode we go with a very short default (SNAPSHOT images
        # should practically arrive within the 1st second after exposure).
        # Triggered modes (SINGLE, DOUBLE) receive a larger timeout.
        # If set to <= 0.0, deactivate the timeout feature altogether.
        tmp = "5.0" if self._target_op_mode == DetectorOpMode.SNAPSHOT else "300.0"
        self._first_image_overdue = \
            float(self._env.get("EIGER_IMAGE_OVERDUE", tmp))

        self._action_task_pool = {}


    async def startup(self, period=0.01):
        logger.info(f'msg="Starting up Eiger2X"')
        self._api_task = asyncio.create_task(self._api_con.run(self._events, period))
        self._zmq_task = asyncio.create_task(self._zmq_con.run(self._events, period))


    async def teardown(self):
        logger.info(f'msg="Tearing down Eiger2X"')
        self._api_task.cancel()
        self._zmq_task.cancel()
        try: 
            await self._api_task
            await self._zmq_task
        except asyncio.CancelledError: ...


    async def _api_req(self, *a, **kw):
        await self._api_con.req(*a, **kw)

        
    @query_handler(
        Query.GetConfig,
        Query.GetRuntime,
        Query.IsInitialized
    )
    def _queries(self, event):
        return {
            Query.IsInitialized: InitStateEvent(self._setup_finished),
            
            Query.GetRuntime: RuntimeStateEvent(self._api_con.eiger_runtime) \
            if self._api_con.eiger_is_initialized \
            else ErrorEvent(f'Device not initialized'),
            
            Query.GetConfig: ConfigStateEvent(self._api_con.eiger_config) \
            if self._api_con.eiger_is_initialized \
            else ErrorEvent(f'Device not initialized')

        }[event.query]


    @command_task(Command.Initialize)
    async def _run_initialize(self, cmd):

        _opmode = lambda x: _detector_op_mode_names[x]

        try:
            while not self._api_con.eiger_is_initialized:
                await asyncio.sleep(0.001)

            logger.info(f'msg="Eiger initialilzed, configuring now" '
                        f'opmode={_opmode(self._target_op_mode)}')

            settings = _eiger_opmode_settings[self._target_op_mode]

            for k,v in settings.items():
                logger.info(f'param="{k[0]}.{k[1]}.{k[2]}" setting="{v}"')

                sub, grp, dt = k
                result = await self._api_req(
                    EigerConfigRequest(detail=dt, value=v, subsystem=sub, group=grp)
                )

            #logger.info(f'msg="Eiger is {self._api_con.eiger_runtime.raw_state}"')
            while not self._api_con.eiger_is_ready:
                await asyncio.sleep(0.001)
            logger.info(f'msg="Setup finished" raw_state={self._api_con.eiger_runtime.raw_state}')

            self._setup_finished = True
            
        except Exception as e:
            logger.error(f'msg="Initialization failed, details follow"')
            logger.error(e)


    @command_task(Command.Acquire)
    async def _run_acquire(self, cmd, duration):

        t0 = time.time()
        logger.info(f'msg="Acquiring" duration="{duration}"')
        
        try:
            #await self._api_req(DisarmRequest())
            
            ct = CountTimeRequest(duration, gfreq=self.gating_frequency,
                                  mode=self._api_con.eiger_config.op_mode)
            
            await self._api_req(ct)
            
            await self._api_req(ArmRequest())
            
            # trigger/disarm only necessary for explicit (internal) triggering,
            # with external trigger the data stream messages will just pour in.
            if self._api_con.eiger_config.op_mode == DetectorOpMode.SNAPSHOT:
                await self._api_req(TriggerRequest())
                await self._zmq_con.wait_for_stream_begin(
                    timeout=duration+self._first_image_overdue
                )
                await self._api_req(DisarmRequest())

        except Eiger2XStreamTimeout as e:
            logger.error(f'msg="Timeout waiting for exposure" duration="{duration}"')
            await self._api_con.req(DisarmRequest())
            self.push_event(ErrorEvent("Timeout waiting for data stream"))

        except asyncio.CancelledError as e:
            uuid = self._zmq_con.mark_as_cancelled()
            self._events.push(CancelDataEvent(series_uuid=uuid))
            raise

        except Exception as e:
            logger.error(f'msg="Acquisition error, detail follows"')
            logger.error(e)
            self.push_event(ErrorEvent(str(e)))

        finally:
            t = time.time()-t0
            logger.info(f'msg="Acquisition finished in {t:.3f} seconds"')


    @command_task(Command.Clear)
    async def _run_clear(self, cmd):
        logger.info(f'msg="Nothing to do on h/w driver level."')


    @command_task(Command.Cancel)
    async def _run_cancel(self, cmd):
        uuid = self._zmq_con.current_uuid

        if uuid is None:
            logger.info(f'msg="Ignoring cancel request for non-existent series UUID" uuid="{uuid}"')
            return CommandResultState(event.command, CommandResult.Success)
        
        logger.info(f'msg="Cancelling acquision series" uuid="{uuid}"')
        # Because of a BRAIN FUCKED API DECISION in the Eiger labs (the
        # "trigger" command will not receive a HTTP response until AFTER the
        # integration time has passed), aborting a request will leave a
        # dangling coroutine when cancelled. (To be fair, this is also coupled
        # with what is likely a bug in aiohttp.)
        #
        # In any case, in order to get the thread to move on, passing "disarm"
        # command apparently wakes up the device and allows the coroutine to
        # continue -- and be cancelled as it should.
        await self._api_con.req(AbortRequest())
        await self._api_con.req(DisarmRequest())        


    @command_task(Command.ChannelAdjust)
    async def _run_chadjust(self, cmd, channel_name=None, **params):
        ## Adjusts channel parameters.
        ## Currently this is only "threshold_energy" (defined in Eiger2XApiConnector).
        ## channel_name here is something like `channel_{id}`

        
        try:
            
            chid = self._api_con._chid_from_label(channel_name)

            settings = {
                tuple([p.format(chid=chid) for p in self._api_con._channel_meta_format[pkey]]):val \
                for pkey,val in params.items()
            }

            for (sub,grp,det),val in settings.items():
                logger.debug(f'subsystem={sub} group={grp} detail={det} value={val}')

            delayed = [
                self._api_req(
                    EigerConfigRequest(subsystem=sub, group=grp, detail=det, value=v)
                ) for ((sub,grp,det),v) in settings.items()
            ]

            await asyncio.gather(*delayed, return_exceptions=False)

        except Exception as e:
            logger.error(e)
            raise
