# timing_decorator/timer.py

import time
import functools

def timeit(func):
    """Decorator to measure execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        print(f"Function '{func.__name__}' executed in {duration:.4f} seconds")
        return result
    return wrapper
