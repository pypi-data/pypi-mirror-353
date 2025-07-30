# timing_decorator/timer.py

import time
import functools
from rich.console import Console
from rich.panel import Panel
import asyncio

console = Console()

def timeit(tag=None):
    """
    Decorator to measure execution time of a function.
    
    Args:
        tag (str, optional): A tag to identify the function in the output. 
                           If not provided, the function name will be used.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            duration = end - start
            
            display_name = tag if tag is not None else func.__name__
            console.print(Panel(
                f"Function '{display_name}' executed in {duration:.4f} seconds",
                title="⏱️  Timing Results",
                border_style="blue"
            ))
            return result
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            duration = end - start
            
            display_name = tag if tag is not None else func.__name__
            console.print(Panel(
                f"Function '{display_name}' executed in {duration:.4f} seconds",
                title="⏱️  Timing Results",
                border_style="blue"
            ))
            return result
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator
