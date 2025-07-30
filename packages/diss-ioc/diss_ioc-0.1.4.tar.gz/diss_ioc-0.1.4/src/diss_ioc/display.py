from matplotlib import pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

import time, math, logging

logger = logging.getLogger(__name__)

class MatplotlibDisplay:
    '''
    Stupidly simple class that uses Matplotlib to visualize 2D numpy arrays.
    '''
    def __init__(self, *panel_names, initialize=True, flip_lr=True):
        if initialize:
            self.init_display(panel_names if panel_names is not None \
                              else ('lolek', 'bolek'))

        self.flip_lr = flip_lr

    def init_display(self, *panel_names, rows=None, cols=None):
        self.panelNames = panel_names
        
        rows = rows if rows is not None else (int(math.ceil(math.sqrt(len(self.panelNames)))))
        cols = cols if cols is not None else int(math.ceil(len(self.panelNames)/rows))
        logger.info(f'geometry={rows}x{cols} '
                    f'displays={self.panelNames}')
        
        self.figure = plt.figure()
        
        self.axes = { k: self.figure.add_subplot(rows, cols, i+1) \
                      for i,k in enumerate(self.panelNames) }
        
        self.panels = { k: x.imshow(np.zeros([2,2]), norm=LogNorm(vmin=1, vmax=4e9)) \
                        for k, x in zip(self.panelNames, self.figure.axes)
                       }

        for k,ax in self.axes.items():
            ax.set_title(k)

        # caching some data array metrics for autoscaling
        self.last_update = {k:time.time() for k in self.panelNames }
        
        self.figure.show(True)


    @property
    def is_initialized(self):
        return hasattr(self, "figure")
        

    def update(self, panel, data=None):
        try:
            ax = self.axes[panel]
        except KeyError:
            logging.error("%s: no such display panel" % panel)
            return
        
        if data is None:
            return

        if self.flip_lr:
            img = data[:,::-1]
        else:
            img = data
        
        self.panels[panel].set_data(img)
        self.panels[panel].set_extent((0, img.shape[1], 0, img.shape[0]))
        self.figure.canvas.draw_idle()

        # just for benchmarking.
        tnow = time.time()
        tdiff = tnow - self.last_update[panel]
        self.last_update[panel] = time.time()


    def handle_events(self):
        self.figure.canvas.flush_events()
