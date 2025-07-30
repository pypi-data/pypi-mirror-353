import asyncio, logging, sys, os, importlib, traceback, math, \
    itertools, time, string, random
from diss_ioc.application import EigerApplication
from diss_ioc.event import DetectorState
from diss_ioc.pvgroup import PvTopLevel

from caproto.asyncio.server import Context as ServerContext
from caproto.asyncio.server import start_server

logger = logging.getLogger("diss_ioc")

class IocApplication(EigerApplication):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)


    async def run_step(self):
        return await asyncio.gather(super().run_step(),
                                    return_exceptions=False)


    async def _wait_for_device(self, state=DetectorState.READY, timeout=300.0):
        t0 = time.time()
        last_state = None
        while (time.time()-t0 < timeout) and (timeout>0):
            if self._ctl.state == state:
                logger.info(f'msg="Detector ready" state="{self._ctl.state_name}"')
                return
            elif last_state != self._ctl.state:
                last_state = self._ctl.state
                logger.info(f'msg="Waiting for initialization" state="{self._ctl.state_name}"')

            await asyncio.gather(self.run_step(),
                                 asyncio.sleep(0.1),
                                 return_exceptions=False)
                
        raise RuntimeError(f'msg="Detector fails to come up" '
                           f'state="{self._ctl.state_name}"')

    
    async def _start_ioc(self, prefix=None):
        if prefix is None:
            rnd = ''.join(random.choices(string.ascii_uppercase, k=6))
            prefix = self._env.get('DISS_EPICS_PREFIX', f'{rnd}:')
            
        self._pvtop = PvTopLevel(prefix=prefix, detector=self._ctl)
        self.set_data_sink(self._pvtop._update_eiger_data)
        
        for pv,obj in self._pvtop.full_pvdb.items():
            logger.info(f'pv="{pv}"')
        self._ioc = asyncio.create_task(start_server(self._pvtop.full_pvdb))
        logger.info(f'msg="IOC running" prefix=\"{prefix}\""')


    async def run_init(self):
        try:
            await super().run_init()
            await self._wait_for_device()
            await self._start_ioc()
        except Exception as e:
            logger.error(f'msg="Initialization failure" error="{e}"')
            raise


def main(args=None, env=None):
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    app = IocApplication(args=(args if args is not None else sys.argv),
                         env=(env if env is not None else os.environ))

    asyncio.run(app.run(period=0.01))


if __name__ == "__main__":
    main()
