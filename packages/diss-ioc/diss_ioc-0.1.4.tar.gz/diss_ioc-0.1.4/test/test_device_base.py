
from diss_ioc.controller import (
    ControllerEngine,
    Query,
    Command,
    EventQueue,
)

from diss_ioc.devices.base import (
    DeviceEngineBase,
    command_task,
)

from contextlib import suppress

from diss_ioc.devices.sim import DeviceEngine

import asyncio, sys, pytest, traceback, time, random

from .conf_tools import run_queue, QTask


class Foo(DeviceEngineBase):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._init_done = 0


    @command_task(Command.Initialize)
    async def _do_init(self, cmd, foo=None, moo=None):
        self._init_done += 1


    def moron(self):
        pass


def test_create_foo():
    f = Foo(None)


class TestEngineBase:
    @pytest.fixture
    async def qpack(self, dev_engine_type):
        q = QTask("cmd",
                  dev_engine=dev_engine_type,
                  ctl_engine=ControllerEngine)
        yield q
        await q.die()

        
class TestCommandDecorator(TestEngineBase):

    @pytest.fixture
    def dev_engine_type(self):
        return Foo

    
    async def test_cmd_task(self, qpack):
        print('stuff:', qpack)

        from diss_ioc.devices.sim import DeviceEngine as SimDevice

        s = SimDevice(qpack.queue)

        await asyncio.sleep(1.0)
        qpack.ctl.push_command(Command.Initialize)
        await asyncio.sleep(1.0)

        assert qpack.dev._init_done > 0
