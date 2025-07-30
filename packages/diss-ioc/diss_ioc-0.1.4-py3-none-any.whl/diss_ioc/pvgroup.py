import asyncio, logging, sys, os, importlib, traceback, math, itertools, time

from caproto.server import PVGroup, pvproperty, PVSpec
from caproto import ChannelData, ChannelDouble, ChannelInteger, ChannelString, \
    SkipWrite

import numpy as np

from diss_ioc.event import DetectorState #, _detector_op_mode_names
from diss_ioc.controller import _state_names

from functools import partial


logger = logging.getLogger(__name__)

class PvChannel(PVGroup):
    '''
    PVs associated with an eiger image channel.

    An image channel (typically a "threshold" in Eiger terminology)
    may usually have 1 or 2 images, depending on the operational mode
    (single or double). A typcal device may entertain more than one channel
    (2 is common).
    '''
    asize0 = pvproperty(value=1)
    asize1 = pvproperty(value=1)
    asize2 = pvproperty(value=1)

    ## The 'image' field needs to be dynamic
    ## We also make the 'meta' fields dynamic (device-dependent extra info)


    def __init__(self, parent, name, num_images, width, height, channel_name=None,
                 **meta):
        '''
        Initialize channel-specific PV group.

        Args:
            parent: Detector PV-group this channel PV-group belongs to
            name: Name of the channel PV section (mandatory, this will
              serve to construct the actual EPICS prefix for this channel,
              by the format "{top_prefix}{name}")
            num_images: Number of images expected. Together with
              `width` and `height` this dictates the shape of the
              data array.
            width: Size of the slowest data-changing dimension
            height: Size of the fasterst data-changing dimension
            channel_name: if this is not `None`, it is used as the name
             of the channel as known to the detector itself. If `None`,
             the same as `name` is assumed.
        '''
        self.name = name
        self.channel_name = channel_name if channel_name is not None else name
        self.prefix = f'{parent.prefix}{self.channel_name}:'
        
        self.detector_pvgroup = parent
        self.data_shape = (num_images, width, height)
        
        max_data = num_images * width * height
        self._data_pv = PVSpec(name="image", value=[0]*max_data,
                               dtype=float, max_length=max_data)

        self._meta_pv = {
            f'{self.prefix}{k}': PVSpec(name=f"{k}", value=v,
                                        put=partial(self._put_channel_meta, k)) \
            for k,v in meta.items()
        }
        
        logger.info(f'msg="Registering channel with EPICS" channel="{self.name}"')
        super().__init__(self.prefix, name=self.name)

        self._dynamic_pvdb = {
            k:s.create(group=None) for k,s in self._meta_pv.items()
        }

        self._image_pv = self._dynamic_pvdb[f'{self.prefix}image'] = \
            self._data_pv.create(group=None)


    async def _update_channel_meta_if_new(self, key, value):
        # Called then a channel meta-value receives new data via detector
        # -> need to update EPICS, if not already up to date
        pv = self._dynamic_pvdb[f'{self.prefix}{key}']
        if pv.value != value:            
            await pv.write(value, verify_value=False)


    async def _put_channel_meta(self, meta_key, pvinst, value):
        ## Called when a channel meta-value receives new data via EPICS
        ## -> needs to update detector.
        logger.debug(f'channel="{self.channel_name}" '
                     f'key="{meta_key}" '
                     f'msg="Setting meta parameter" '
                     f'value="{value}"')
        await self.detector_pvgroup._put_channel_meta(self.channel_name, meta_key, value)
        raise SkipWrite()
        

    @asize0.startup
    async def _startup(self, inst, alib):
        await asyncio.gather(*[self.asize0.write(self.data_shape[0]),
                               self.asize1.write(self.data_shape[1]),
                               self.asize2.write(self.data_shape[2])],
                             return_exceptions=False)


    @property
    def full_pvdb(self):
        pvdb = self.pvdb.copy()
        pvdb.update(self._dynamic_pvdb)
        return pvdb


class PvTopLevel(PVGroup):
    '''
    Top-level PV container / handler class (CAproto based)
    '''

    #mode     = pvproperty(value="n/a", max_length=40, report_as_string=True,
    #                      doc="IOC work-mode (snapshot, single, double)")
    
    state    = pvproperty(value="n/a", max_length=40, report_as_string=True,
                          doc="Current state of the detector controller")

    ssqcnt   = pvproperty(value=-1, doc="Short-sequence frame counter")

    uuid     = pvproperty(value='21b427ff-d5a9-4d3b-a6c1-ffb17536e884', max_length=40,
                          report_as_string=True, doc="Image UUID")

    numid    = pvproperty(value=-1, doc="Numerical image sequence ID")


    acquire  = pvproperty(value=0, doc="Trigger a new image acquisition in current mode")
    
    duration = pvproperty(value=1.0, doc="Duration in seconds of the next acquisition")
    
    cancel   = pvproperty(value=0, doc="Cancel current acquisition")
    
    clear    = pvproperty(value=0, doc="Clear current error list")
    
    error    = pvproperty(value='', max_length=40, report_as_string=True,
                          doc="The last available error")
    
    def __init__(self, prefix, *a, detector=None, **kw):
        super().__init__(prefix=prefix, *a, **kw)
        self.detector = detector
        eiger_conf = self.detector.config
        self.channels = {
            c.label:PvChannel(parent=self,
                              name=c.label,
                              num_images=eiger_conf.num_images,
                              width=eiger_conf.image_size[0],
                              height=eiger_conf.image_size[1],
                              **(c.meta)) \
            for c in eiger_conf.channels
        }

        # aqduration and start_ts are dynamic (depending on num_images and num_channels),
        # so we need to create them like this
        max_data = eiger_conf.num_images * len(eiger_conf.channels)

        logger.info(f'msg="Extra dynamic info" length={max_data}')
        
        self.start_ts = \
            PVSpec(name=f"{prefix}start_ts", value=[0.0]*max_data,
                   dtype=type(time.time()), max_length=max_data)\
            .create(group=None)

        self.acq_td = \
            PVSpec(name=f"{prefix}acq_td", value=[0.0]*max_data,
                   dtype=float, max_length=max_data)\
            .create(group=None)            

        # extra controller data to write per-frame.
        # Key: data key (in controller feedback),
        # Val: pv name here in PVgroup
        self.extra_data = {
            'ssqcnt': 'ssqcnt',
            'uuid': 'uuid',
            'numid': 'numid',
            'start_ts': 'start_ts',
            'duration': 'acq_td'
        }
        
        
        self.detector.add_state_hook(self._update_eiger_state)
        
        self.detector.add_state_hook(self._update_eiger_errors, when_in=[DetectorState.ERROR,
                                                                         DetectorState.FAIL])
        
        self.detector.add_state_hook(self._clear_actions, when_in=[DetectorState.READY,
                                                                   DetectorState.INTEGRATE])

        self.detector.add_channel_meta_hook("ioc", self._update_eiger_channel_meta)


    async def _put_channel_meta(self, channel, key, val):
        self.detector.set_channel_meta(channel, key, val)


    #@mode.startup
    #async def _startup(self, pvinst, alib):
        #om = self.detector.config.op_mode
        #mname = _detector_op_mode_names[om]
        #await asyncio.gather(self.mode.write(mname),
        #                     return_exceptions=True)
    #    pass


    async def _update_eiger_state(self, state, event, enter):
        # Called on every state run (meant to update on enter only)
        if not enter:
            return
        sname = _state_names[state]
        if enter or (sname != self.state.value):
            await self.state.write(sname)


    async def _update_eiger_errors(self, state, event, enter):
        # Called when detector is in ERROR or FAIL
        if not enter:
            return
        elist = self.detector.errors()
        if len(elist):
            err = str(elist[-1])[0:38]
            if self.error.value != err:
                await self.error.write(err)

    
    async def _update_eiger_channel_meta(self, channel_name, meta_dict):
        # Called when any of the Eiger channels receives new metadata.
        wlist = []
        chobj = next(iter(filter(lambda x: x.label == channel_name,
                                 self.detector.config.channels)))
        chpv = self.channels[channel_name]
        for key,val in chobj.meta.items():
            wlist.append(chpv._update_channel_meta_if_new(key, val))
        await asyncio.gather(*wlist, return_exceptions=False)


    


    async def _clear_actions(self, state, event, enter):
        ## Clears a bunch of "action flags", i.e. PVs which trigger
        ## actions when set to 1.
        
        async def write_if_different(pv, val):
            if pv.value != val:
                await pv.write(val)
                
        if state == DetectorState.READY and enter==True:
            await asyncio.gather(write_if_different(self.acquire, 0),
                                 write_if_different(self.clear, 0),
                                 write_if_different(self.cancel, 0),
                                 return_exceptions=False)
            
        elif state == DetectorState.INTEGRATE and enter==True:
            await asyncio.gather(write_if_different(self.acquire, 1),
                                 write_if_different(self.cancel, 0),
                                 return_exceptions=False)


    async def _update_eiger_data(self, data):
        try:

            #ret = await asyncio.gather(*[cobj._image_pv.write(data[name].flatten()) \
            #                             for name,cobj in self.channels.items()])            
            
            # There are two sets of data keys in `data`:
            #   - image data (channel name as key), one per channel
            #   - general info ("uuid", "numid", "ssqcnt", ... -- see frame.py).
            # Here we split the two.
            #print('data:', {k:data[k].shape for k in data.keys()})
            channel_image_data = dict(filter(lambda x: x[0] in self.channels, data.items()))
            device_extra_data = dict(filter(lambda x: x[0] in self.extra_data, data.items()))

            #print('imgs:', {k:channel_image_data[k].shape for k in channel_image_data.keys()})
            #print('xtra:', {k:device_extra_data[k].shape for k in device_extra_data.keys()})

            awaitables = [] + \
                [cobj._image_pv.write(data[name].flatten()) \
                 for name,cobj in self.channels.items()] + \
                [(getattr(self, self.extra_data[name])).write(dat.flatten()) \
                 for name,dat in device_extra_data.items()]

            #print(awaitables)
            
            ret = await asyncio.gather(*awaitables)

            for r,ch in zip(ret,
                            [k for k in channel_image_data.keys()]+
                            [k for k in device_extra_data.keys()] ):
                if isinstance(r, Exception):
                    logger.error('msg="Error sinking data" error="{e}" key="{ch}"')

        except Exception as e:
            logger.error(f'msg="General error sinking data" error="{e}"')
            raise


    @acquire.putter
    async def _start_acquire(self, pvinst, val):
        old_val  = pvinst.value
        det      = self.detector
        duration = self.duration.value
        if (old_val != val) and (val > 0):
            if (det.state == DetectorState.READY):
                logger.info(f'msg="Triggering acquision" value={val} duration={duration}')                
                self._last_acquire = time.time()
                det.acquire(duration=duration)


    @clear.putter
    async def _clear_error(self, pvinst, val):
        if pvinst.value != val and val > 0:
            self.detector.clear()
            await self.error.write('')


    @cancel.putter
    async def _cancel_image(self, pvinst, val):
        if pvinst.value != val and val > 0:        
            self.detector.cancel()


    @property
    def full_pvdb(self):
        db = self.pvdb.copy()
        for cname,cobj in self.channels.items():
            db.update(cobj.full_pvdb.copy())

        db.update({
            self.start_ts.name: self.start_ts,
            self.acq_td.name: self.acq_td
        })
        return db
