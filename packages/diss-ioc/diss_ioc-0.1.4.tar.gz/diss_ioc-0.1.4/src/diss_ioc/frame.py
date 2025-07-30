

import logging, enum, asyncio

from numpy import array, ndarray

logger = logging.getLogger(__name__)

class FrameCollector:
    '''
    Accepts detector data events and puts together a data frame.

    "Frame" is a concept from NX5d we're borrowing here, and roughly
    translates to "one datapoint" -- that is, the images and metadata
    associated with exactly one acquision command. These can be
    several images, and can also be several `ImageDataEvent`
    occurences.
    '''
    
    def __init__(self, cfg=None):
        self._arrays = None
        self._callbacks = {}

        if cfg is not None:
            self.configure(cfg)

        # This runs from 0 to 15 for every image that runs through the state machine.
        # It can be used to detect (short-range) image skips.
        self._col_seq_cnt = 0


    @property
    def is_configured(self):
        return hasattr(self, "_device_config") and \
            (self._device_config is not None)


    @property
    def numid(self):
        return self._arrays['numid']


    @property
    def uuid(self):
        return self._arrays['uuid']
    
            
    def add_callback(self, label, proc):
        '''
        Adds a data-sink callback, i.e. function of the signature
        `proc(arary_dict)`.
        The function called when a frame is finished. The array
        typically has the following fields:
          - "numid": a numerical frame ID, 1D array with single element
          - "uuid": an UUID for the frame, 1D array with single element
          - "start_ts": start timestamp for image integration,
            2D array of the shape (channel, )
        '''
        self._callbacks[label] = proc
        return label


    async def callback(self):
        await asyncio.gather(*[p(self._arrays) for l,p \
                               in self._callbacks.items()],
                             return_exceptions=True)


    def reset(self):
        self._arrays = None


    def start(self, img_size, num_images, channel_names, se):
        '''
        Initializes a new collection session.
        '''
        # Shape in the final dataset ("run"):
        #   image: (frame, image_index, image_w, image_h)
        #   times: (frame, image_index)
        #   IDs:   (frame)
        #          (frame)
        # At this level we drom the "frame", so we're stuck with
        # dimension N-1 (3D for images, 2D for times, 1D for other
        # StartDataEvent-level metadata).

        if self._arrays is not None:
            raise RuntimeError(f'msg="Collector session already active" '
                               f'old={self.uuid} new={se.uuid}')
        else:
            logger.info(f'msg="New collector" uuid="{se.uuid} ssqcnt={self._col_seq_cnt}"')

        img_shape = [ num_images ] + img_size
        t_shape   = [ num_images ] + [1]
        id_shape  = [ 1 ]

        self._arrays = {
            'start_ts': ndarray(t_shape, dtype=float),
            'duration': ndarray(t_shape, dtype=float),
        }
        self._arrays.update({
            c:ndarray(img_shape, dtype=float) for c in channel_names
        })

        self._arrays['uuid'] = array(str(se.uuid))
        self._arrays['numid'] = array(se.numid)
        self._arrays['ssqcnt'] = array(self._col_seq_cnt)
        self._col_seq_cnt = (self._col_seq_cnt+1) % 16

        self._arrays.update({
            k:array(str(v)) for k,v in se.meta.items()
        })


    def add_image(self, e):
        if str(e.series_uuid) != self.uuid:
            raise RuntimeError(f'msg="Stray image / wrong series" '
                               f"want={self.uuid} have={e.series_uuid}")
        
        self._arrays['start_ts'][e.imgid] = e.start_ts
        self._arrays['duration'][e.imgid] = e.duration
        
        for ch_name,img_data in e.images.items():
            try:
                channel_store = self._arrays[ch_name]
            except KeyError as e:
                logger.error(f'msg="Unexpected image channel" channel="{ch_name}"')
                raise
            a = channel_store[e.imgid].shape
            b = img_data.shape
            channel_store[e.imgid][:] = img_data[:]
                    

    def finish(self, e):
        if str(e.series_uuid) != self.uuid:
            raise RuntimeError(f"want={self.uuid} have={e.series_uuid} "
                               f'msg="Stray frame closure"')
        # nothing else to do for now


    async def finish_and_callback(self, e, reset=True):
        self.finish()
        if exec_callbacks:
            await self._callback(self._arrays)
        if reset:
            self.reset()
        
    
    async def __call__(self, state, e, enter):

        if not self.is_configured:
            raise RuntimeError(f'msg="FrameCollector lacks device config"')
        
        if isintance(e, StartDataEvent):
            self.start(self._device_config.image_size,
                       self._device_config.num_images,
                       self._device_config.channels.keys(),
                       e)
            
        elif isinstance(e, ImageDataEvent):
            self.add_image(e)
            
        elif isinstance(e, EndDataEvent):
            await self.finish_and_callback(e)
            
        elif isinstance(e, CancelDataEvent):
            self.reset()
