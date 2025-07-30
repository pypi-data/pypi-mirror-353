from function_timing_decorator import timeit
import time
import asyncio

@timeit(tag="test")
def test_sync():
    time.sleep(0.1)

@timeit(tag="test_async")
async def test_async():
    await asyncio.sleep(0.1)

def test_all():
    test_sync()
    asyncio.run(test_async())
