import enum, logging, asyncio

from uuid import uuid4

logger = logging.getLogger(__name__)

__all__ = [
    "DetectorState",
    "NewState",
    
    "Event",
    
    "RequestEvent",
    "StateEvent",
    "DataEvent",

    "StartDataEvent",
    "EndDataEvent",
    "ImageDataEvent",
    "CancelDataEvent",

    "Command",
    "CommandResult",
    "CommandRequest",
    "CommandException",
    "ChannelAdjustCommandRequest",
    "AcquireCommandRequest",
    "CommandResultState",

    "Query",
    "QueryRequest",

    "InitStateEvent",
    "ConfigStateEvent",
    "RuntimeStateEvent",
    "ChannelStateEvent",

    "ErrorEvent",

    "DetectorEngineRole",
    #"DetectorOpMode",

    "EventQueue",

    "DeviceState",
    "DeviceConfig",
    "DeviceRuntime",
    "ChannelConfig",
]


class DetectorState(enum.IntEnum):
    INIT = 0      # default state at start / after turn-on
    WARMUP = 1    # Hardware initialization process

    # ACHTUNG, the numerical values are used in DetectorEngine.__init__
    # to determine status/config queries. Specifically, everything that
    # is only permitted in the initial phase must have a numerical ID
    # lower than .READY
    
    READY = 2     # ready to accept commands, no other work executing
    INTEGRATE = 4 # making images
    PROCESS = 5   # done with imaging, not yet read for new images
    CANCEL = 6    # current imaging/integrating canceled, results void
    ERROR = 7     # something went wrong, results void, need user-ack
    FAIL = 8      # fatal, irrecoverable error
    

class NewState(Exception):
    '''
    Used to switch states: the state procs in `DetectorEngine` are implemented
    using the same formalism as the hooks. Generally, hooks are expected to return
    messages to post to the queue.

    State procs (using the hook formalism) will raise, or return, `StateSwitch`
    instead when they need to switch states.
    '''
    def __init__(self, new_state, *evlist, events=None):
        self.state = new_state
        self.events = [e for e in evlist]
        if events is not None:
            self.events += events


class Event:
    ''' Base class for all Detector events '''
    pass

class RequestEvent(Event):
    ''' Base class for Request events -- essentially everything we send to DEVICE '''
    pass


class StateEvent(Event):
    '''
    Base class for non-data events sent from device to CONTROLLER.
    These are usually always in reply to a specific request.
    '''
    pass


class DataEvent(Event):
    '''
    Base class for data events sent from device to CONTROLLER.
    
    These are not necessarily in reply to a request, they're the
    result of device activity. (The activity itself may have been
    triggered by a `RequestEvent`, but none of the data events
    are actual driect replies to that request.)
    '''
    pass


class StartDataEvent(DataEvent):
    def __init__(self, numid=None, uuid=None, **meta):
        super().__init__()
        self.numid, self.uuid = (
            int(numid if numid is not None else 0),
            uuid if uuid is not None else uuid4()
        )
        self.meta = meta.copy()


    def __str__(self):
        return f'{self.__class__.__name__}[{self.numid}, {self.uuid}]'


    def __repr__(self):
        return self.__str__()

    
class ImageDataEvent(DataEvent):
    def __init__(self, imgid, series_uuid,
                 start_ts=None, duration=None,
                 data_dict=None, **data):
        super().__init__()
        self.imgid = imgid
        self.series_uuid = series_uuid
        self.start_ts = start_ts
        self.duration = duration
        self.images = {}

        if data_dict is None:
            data_dict = {}
        data_dict.update(data)

        for k,v in data.items():
            self.add_image(k, v)


    def __str__(self):
        imgs = [f'{k}={v.shape}' for k,v in self.images.items()]
        return (f'{self.__class__.__name__}['
                f'id={self.imgid}, '
                f'{", ".join(imgs)}, '
                f'series={self.series_uuid}]')


    def __repr__(self):
        return self.__str__()


    def add_image(self, channel, data):
        '''
        Adds an image for `channel` to the current event.
        Note that a datapoint frame may contain _several_
        events!
        '''
        if channel in self.images:
            raise RuntimeError(f'channel="{channel}" image_id="{self.seqid}"'
                               f' msg="Already have image for channel"')
        
        self.images[channel] = data
    

class EndDataEvent(DataEvent):
    def __init__(self, series_uuid):
        self.series_uuid=series_uuid

    def __str__(self):
        return f'{self.__class__.__name__}[{self.series_uuid}]'

    def __repr__(self):
        return self.__str__()
        
        

class CancelDataEvent(DataEvent):
    '''
    Sent when an image acquisition process has been cancelled.
    '''
    def __init__(self, series_uuid):
        self.series_uuid=series_uuid

    def __str__(self):
        return f'{self.__class__.__name__}[{self.series_uuid}]'

    def __repr__(self):
        return self.__str__()        
        

class Command(enum.IntEnum):
    # Commands that "do stuff", no parameters
    Initialize = 0  ## Trigger initialization sequence
    Acquire    = 1  ## Arm (external) trigger
    Cancel     = 2  ## Cancel current exposure / trigger waiting
    Clear      = 3  ## Clear any errors, if necessary

    ## These are not implemented because we currently go by
    ## the "preset" philosophy: i.e. every combination of measurement
    ## modes is done by selecting a corresponding preset from a list
    ## and preparing/setting up the device in the corresponding manner
    ## is a hardware driver detail, not an API detail at this level.
    #Setup      = 4  ## Modify a setup parameter (not implemented)
    #SetMode    = 5  ## Switch modes (not implemented)

    ChannelAdjust = 4  ## Adjust a channel meta-parameter


_Command_i2n = {
    getattr(Command, k):k for k in \
    filter(lambda i: not i.startswith('_'),
           Command.__dict__)
}
    

class CommandResult(enum.IntEnum):
    # return values for command ack
    Failed = 0
    Success = 1


class CommandRequest(RequestEvent):
    ''' Ask the device to execute a predefined command '''
    def __init__(self, command, pdict=None, **params):
        self.command = command
        self.params = pdict.copy() if pdict is not None else {}
        self.params.update(params)

    def __repr__(self):
        return f'CommandRequest.{_Command_i2n[self.command]}' \
            f'{[k for k in self.params.keys()]}'


class ChannelAdjustCommandRequest(CommandRequest):
    def __init__(self, channel, **meta):
        super().__init__(Command.ChannelAdjust, channel_name=channel, **meta)

    
class AcquireCommandRequest(CommandRequest):
    ''' Dedicated command type for image acquisition '''
    def __init__(self, duration):
        super().__init__(Command.Acquire, duration=duration)


class CommandException(Exception):
    # This is just a transport wrapper for CommandResultState
    # (we can't really raise CommandResultState because that one is
    # not derrived from Exception, but some workflows are better
    # if we can raise)
    def __init__(self, cmd_result_state):
        self.cmd_result_state = command_result

        
class CommandResultState(StateEvent):
    ''' Sent in reply to a CommandRequest '''
    def __init__(self, cmd, state, detail=None):
        super().__init__()
        self.command = cmd
        self.state = state
        self.detail = detail


        
class Query(enum.IntEnum):
    # State-query commands; they don't trigger state changes in the
    # defice, they just report on various parameters.
    IsInitialized = 4  ## Triggers a reporting init-state query (InitStateEvent)
    GetConfig     = 5  ## Triggers a reporting of the config-state (ConfigEvent)
    GetRuntime    = 6  ## Triggers a reporting of the config-state (ConfigStateEvent)


_Query_i2n = {
    getattr(Query, k):k for k in \
    filter(lambda i: not i.startswith('_'),
           Query.__dict__)
}

class QueryRequest(RequestEvent):
    def __init__(self, query):
        self.query = query
        self._name = _Query_i2n[self.query]

    def __repr__(self):
        return f'QueryRequest.{self._name}'


class InitStateEvent(StateEvent):
    ''' Signalized (a change in) the current init state of the hardware '''

    initialized = False
    
    def __init__(self, initialized):
        super().__init__()
        self.initialized = initialized


class ChannelConfig:
    label: str

    # channel meta-information (energy thresholds?)
    # typically these are { 'threshold_enery': xxx },
    # but they can be whatever. this is device dependent
    meta: dict()

    def __init__(self, label, meta_dict=None):
        self.label = label
        self.meta = meta_dict.copy() if meta_dict is not None else {}


    def __eq__(self, other):
        if len(self.meta) != len(other.meta):
            return False
        for k,v in self.meta.items():
            if k not in other.meta:
                return False
            if other.meta[k] != v:
                return False
        return self.label == other.label
            


class DeviceState(enum.IntEnum):
    IDLE = 1  # device accepts new acquisition commands
    BUSY = 2  # device cannot accept new acquisiton commands, need to wait
    ERROR = 3 # device dysfunctional, user action required


class DeviceConfig:
    channels = []          # array of channel config
    image_size = [ 0, 0 ]  # in pixels
    pixel_size = [ 0, 0 ]  # in meter
    num_images = 0

    def __repr__(self):
        return f'DeviceConfig(' \
            f'channels={[c.label for c in channels]},  '\
            f'image_size={self.image_size}, '\
            f'pixel_size={self.pixel_size} '\
            f'num_images={self.num_images} '\
            f')'

    #@property
    #def num_images(self):
    #    return {
    #        DetectorOpMode.SNAPSHOT: 1,
    #        DetectorOpMode.SINGLE: 1,
    #        DetectorOpMode.DOUBLE: 2
    #    }[self.op_mode]


class DeviceRuntime:
    state = None     # should be DeviceState
    raw_state = ""   # raw state reported by device    
    erors = []       # list of currently active errors


class ConfigStateEvent(StateEvent):
    # Holds information together about "static" device config data
    # DeviceEngine updates this on every loop run once it reaches
    # READY state and beyond.
    config: DeviceConfig

    def __init__(self, cfg):
        super().__init__()
        if cfg is not None:
            self.config = cfg
        else:
            self.config = None


    @property
    def valid(self):
        return self.config is not None


class RuntimeStateEvent(StateEvent):
    # Similar to ConfigStateEvent, but only for runtime data
    runtime: DeviceRuntime
    def __init__(self, obj):
        super().__init__()
        self.runtime = obj


class ChannelStateEvent(StateEvent):
    # Similar to ConfigStateEvent, but only for data
    # pertaining to a specific channel. Generally, channel
    # (meta)-data can change at any time. Full Config data,
    # in particular data about operation mode, image size
    # and number and names of channels, should never change
    # once the application leaves WARMUP mode.
    channel: str
    meta: dict()
    def __init__(self, channel, **meta):
        super().__init__()
        self.channel = channel
        self.meta = meta.copy()
    

class ErrorEvent(StateEvent):
    detail: str
    fail: bool
    def __init__(self, detail, fail=False):
        self.detail = detail
        self.fail = fail

    def __repr__(self):
        return f'{self.detail}'


class DetectorEngineRole(enum.IntEnum):
    DEVICE = 0
    CONTROLLER = 1


class EventQueue:
    '''
    Manages an event queue to which events can be pushed as they
    are generated, or to which events can be popped for processing.
    '''
    
    class Empty(Exception): pass
    
    def __init__(self):
        self.queue = []


    def pop_role(self, role, raise_empty=True):
        return self.pop(RequestEvent, raise_empty=raise_empty) \
            if role == DetectorEngineRole.DEVICE \
               else self.pop(StateEvent, DataEvent, raise_empty=raise_empty)


    def pop_device(self, raise_empty=True):
        '''
        Pops events meant for a device (i.e. requests).
        '''
        return self.pop_role(DetectorEngineRole.DEVICE, raise_empty)


    def pop_controller(self, raise_empty=True):
        '''
        Pops events meant for the controller (i.e. data and replies).
        '''
        return self.pop_role(DetectorEngineRole.CONTROLLER, raise_empty)


    def pop(self, *types, raise_empty=True):
        for i,e in enumerate(self.queue):
            if len(types)==0:
                return self.queue.pop(i)
            for t in types:
                if isinstance(e, t):
                    return self.queue.pop(i)
        if raise_empty:
            raise self.Empty()


    def push(self, event):
        if isinstance(event, Event):
            self.queue.append(event)
        elif hasattr(event, "__getitem__"):
            self.queue += event
        else:
            raise RuntimeError(f'msg="Unknown event type" event="{event}" type="{type(event)}"')


    def clear(self):
        self.queue.clear()
