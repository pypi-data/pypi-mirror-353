import asyncio
from function_timing_decorator.timer import timeit

@timeit(tag="Synchronous Function")
def sync_function():
    # Simulate some work
    for _ in range(1000000):
        pass
    return "Sync function completed"

@timeit(tag="Async Function")
async def async_function():
    # Simulate some async work
    await asyncio.sleep(1)
    return "Async function completed"

async def main():
    # Test synchronous function
    result1 = sync_function()
    print(f"Result: {result1}")
    
    # Test asynchronous function
    result2 = await async_function()
    print(f"Result: {result2}")

if __name__ == "__main__":
    asyncio.run(main()) 