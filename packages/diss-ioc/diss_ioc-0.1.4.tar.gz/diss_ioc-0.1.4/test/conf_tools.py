import traceback, asyncio, sys, time
from contextlib import suppress

from diss_ioc.controller import (
    ControllerEngine,
    QueryRequest, Query,
    CommandRequest, Command,
    StartDataEvent,
    EventQueue,
    DetectorState
)

async def run_queue(q, period=0.1):
    
    while True:
        try:
            await asyncio.gather(q.dev.step(),
                                 q.ctl.step(),
                                 asyncio.sleep(period),
                                 return_exceptions=False)
            
            print(f'\r'
                  f'ctl={q.ctl.state_name}[{q.ctl.state_age:.2f}] '
                  f'queue={q.queue.queue} ',
                  )
            
            sys.stdout.flush()
            
        except Exception as e:
            print(f'Oops: {e}')
            traceback.print_exc(e)



class QTask:
    def __init__(q, name, ctl_engine=None, dev_engine=None,
                 period=0.1, dev_dict=None, ctl_dict=None):

        print(ctl_engine, dev_engine)
        
        q.queue = EventQueue()
        q.dev_params = (dev_dict if dev_dict is not None else {})        
        q.dev = dev_engine(q.queue, **(q.dev_params))
        q.ctl = ctl_engine(q.queue, **(ctl_dict if ctl_dict is not None else {}))
        q.task = asyncio.create_task(run_queue(q, period), name=name)

    async def die(q):
        with suppress(asyncio.CancelledError):
            q.task.cancel()
            await q.task
