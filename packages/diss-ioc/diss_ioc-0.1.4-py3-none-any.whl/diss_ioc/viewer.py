import asyncio, logging, sys, os, importlib, traceback, math, itertools

logger = logging.getLogger("eiger_ioc")

import diss_ioc.event as det

from diss_ioc.application import EigerApplication
from diss_ioc.display import MatplotlibDisplay

'''
Simple Matplotlib viewer for continuous Eiger image acquisition.
'''

async def print_status(engine):
    print(f'\r{engine.state_name}            \t', end='')


class ViewerApplication(EigerApplication):
    def __init__(self, *args, **kw):
        self._display = EigerDisplay(initialize=False, flip_lr=True)
        kw['sink']=self._display.display_eiger
        kw['stat']=self._display.init_eiger
        super().__init__(*args, **kw)


    async def handle_display(self):
        return self._display.handle_events()


    async def run_step(self):
        return await asyncio.gather(super().run_step(),
                                    self.handle_display(),
                                    return_exceptions=False)


class EigerDisplay(MatplotlibDisplay):

    async def display_eiger(self, data):
        try:
            for k in data.keys():
                if f'{k}0' not in self.panelNames:
                    continue
                for i in range(data[k].shape[0]):
                    self.update(f'{k}{i}', data[k][i].transpose())

        except Exception as e:
            logger.error(f'Failed to display images: {e}')


    async def init_eiger(self, engine):
        if not self.is_initialized and \
           hasattr(engine.config, "channels") and \
           engine.config.initialized:
            chns = []
            for i,c in itertools.product(range(engine.config.num_images),
                                         engine.config.channels):
                    dname = f'{c.label}{i}'
                    logger.info(f'channel={c.label} image_id={i} display={dname}')
                    chns.append(f'{dname}')
            try:
                self.init_display(*chns,
                                  rows=engine.config.num_images,
                                  cols=len(engine.config.channels))
            except Exception as e:
                logger.error(f'msg="Display init failed" error="{e}"')
        await print_status(engine)


def main(args=None, env=None):

    logging.basicConfig()
    logger.setLevel(logging.INFO)

    app = ViewerApplication(args if args is not None else sys.argv,
                            env if env is not None else os.environ)

    asyncio.run(app.run(period=0.01))


if __name__ == "__main__":
    main(sys.argv, os.environ)
