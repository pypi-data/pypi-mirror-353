import pytest, asyncio, string, random, time
import multiprocessing as mp

from diss_ioc.ioc import main as ioc_main

from caproto.asyncio.client import Context as ClientContext

@pytest.fixture
def ioc():

    prefix = '%s:' % ''.join(random.choices(string.ascii_lowercase, k=4))
    p = mp.Process(target=ioc_main,
                   kwargs={
                       'args': [],
                       'env': {
                           'DISS_DEVICE_BACKEND': 'sim',
                           'DISS_EPICS_PREFIX': prefix,
                           'DISS_AUTO_ACQUIRE': 'no',
                           'EIGER_DEVICE_MODE': 'snapshot'
                       }
                   })

    p.daemon = True
    p.start()

    return {
        'prefix': prefix,
        'process': p
    }

@pytest.fixture
async def conn(ioc):
    ctx = ClientContext()
    class Con:
        pass


async def test_chain(ioc):
    print(ioc)
    t0 = time.time()
    while time.time()-t0 > 5.0:
        await asyncio.sleep(0.1)
