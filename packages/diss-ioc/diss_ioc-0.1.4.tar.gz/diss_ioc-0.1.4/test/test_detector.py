
from diss_ioc.controller import (
    ControllerEngine, 
    QueryRequest, Query,
    CommandRequest, Command,
    StartDataEvent,
    EventQueue,
    DetectorState
)

from diss_ioc.devices.sim import DeviceEngine as SimDeviceEngine


import asyncio, sys, pytest, traceback, time, random

from .conf_tools import run_queue, QTask

@pytest.fixture#(scope="module")
async def qtask():
    num_img = random.randint(1, 4)
    q = QTask("QueueRunner",
              dev_engine=SimDeviceEngine,
              dev_dict={
                  'sim_dict': {
                      'num_images': num_img
                  },
              },
              ctl_engine=ControllerEngine,
              ctl_dict={})
    yield q
    await q.die()


class DataReceiver:
    def __init__(self, name=None):
        self.received = False
        self.shapes = {}
        self.name = name if name is not None else "Receiver"

    async def __call__(self, data):
        self.shapes = {k:v.shape for k,v in data.items()}
        self.received = True

    def __bool__(self):
        return self.received


async def test_acquire(qtask):

    rec = DataReceiver("AcqReceiver")
    qtask.ctl.collector.add_callback(rec.name, rec)

    await asyncio.sleep(1.0)
    assert qtask.ctl.state == DetectorState.WARMUP
    
    await asyncio.sleep(6.0)
    assert qtask.ctl.state == DetectorState.READY

    intg_time = 0.5+random.random()*5
    qtask.ctl.acquire(duration=intg_time)
    await asyncio.sleep(0.3)
    assert qtask.ctl.state == DetectorState.INTEGRATE

    # SIM detector can deliver up to 4 images (randomly chosen),
    # and each image will take up to intg_time to "intergrate"
    total_time = qtask.dev_params['sim_dict']['num_images'] * intg_time
    
    await asyncio.sleep(total_time+1.0)
    assert qtask.ctl.state in (
        DetectorState.READY,
        DetectorState.PROCESS,
    )

    assert rec


async def test_cancel(qtask):

    rec = DataReceiver("CancelReceiver")
    qtask.ctl.collector.add_callback(rec.name, rec)
    
    await asyncio.sleep(1.0)
    assert qtask.ctl.state == DetectorState.WARMUP
    
    await asyncio.sleep(6.0)
    assert qtask.ctl.state == DetectorState.READY

    intg_time = 2.0+random.random()*5
    qtask.ctl.acquire(duration=intg_time)
    await asyncio.sleep(0.3)
    assert qtask.ctl.state == DetectorState.INTEGRATE

    qtask.ctl.cancel()
    await asyncio.sleep(1.0)
    
    # Cannot check for "CANCELED" (transition is too fast),
    # but we should be in "READY" shortly after.
    assert qtask.ctl.state in (
        DetectorState.READY,
    )

    assert not rec
