

# Bare Eiger communication application, used only for rapid
# understanding of the communication protocol. Mostly defunct.
# Do not use unless you're in the business of developing
# eiger-ioc internals.

async def do_ints(det, num_images=1, integration_time=1.0):
    await det.set_live_image()
    await det.set_trigger_mode("ints")
    await det.set_ntrigger(1)
    await det.set_nimages(num_images)
    await det.set_count_time(integration_time)

    await det.disarm()
    
    while True:
        await asyncio.sleep(1.0)
        await det.arm()
        await det.arm()        
        print('armed0')
        await asyncio.sleep(1.0)
        print('armed1')
        await det.trigger()
        await asyncio.sleep(integration_time*2.0)
        print('disarming')
        #await det.disarm()
        #await det.next_test_image()
        

async def do_extg(det, mode='single', num_images=1, integration_time=1.0):

    gating_freq=104000.0 # Hz

    await det.set_live_image()

    if mode == 'double':
        await det.set_extg_mode("double")
        await det.set_nimages(num_images)
    elif mode == 'single':
        await det.set_extg_mode("single")
        await det.set_nimages(num_images)
    else:
        raise RuntimeError(f'Nope.')
    
    await det.set_trigger_mode("extg")
    await det.set_counting_mode("normal")
    await det.set_countrate_correction_applied(False)
    await det.set_pixel_mask_applied(False)
    
    await det.set_auto_summation(True)
    await det.set_ntrigger(1)
    await det.set_nexpi(int(integration_time * gating_freq * num_images))
    await det.arm()
    
    while True:
        try:
            await det.wait_for_images(num_images, timeout=-1)
            await det.arm()
        except TimeoutError as e:
            pass
        await asyncio.sleep(0.01)

        

async def do_display(det, num_images=1):
    dis = LiveDisplay()
    displays = ('lolek', 'bolek')
    
    while True:
        try:
            img = await det.pop_images(num_images, timeout=0.0)
            for i,d in zip(img,displays):
                print(f'display={d} image={i.shape} total={len(img)} '
                      f'count={i.sum()} avg={i.mean()}')
                dis.update(d, i)
        except TimeoutError as e:
            pass
        dis.handle_events()
        await asyncio.sleep(0.01)
        

async def det_loop(det, period=0.01):
    while True:
        await asyncio.gather(det.update(),
                             asyncio.sleep(period),
                             return_exceptions=False)

async def run(det, period=1.0):
    await det.init()
    
    try:
        await asyncio.gather(det_loop(det, period),
                             do_ints(det, num_images=2, integration_time=3.0),
                             #do_extg(det, mode='double', num_images=2, integration_time=3.0),
                             do_display(det, num_images=2),
                             return_exceptions=False)

    except Exception as e:
        print(f'Oops: {e}')
        raise


def main():
    det = Detector('10.200.49.175')
    asyncio.run(run(det, period=0.0001))


if __name__ == "__main__":
    main()
