import inspect
from time import time
from typing import Callable
from functools import wraps
from logger import message_logger as mes_log


def timer(func: Callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        st = time()
        result = await func(*args, **kwargs)
        mes_log.warning(
            f'{func.__name__!r} func was executed '
            f'for {round((time() - st), 3)!r} second(s)'
        )
        return result
    

    @wraps(func)
    def wrapper(*args, **kwargs):
        st = time()
        result = func(*args, **kwargs)
        mes_log.warning(
            f'{func.__name__!r} func was executed '
            f'for {round((time() - st), 3)!r} second(s)'
        )        
        return result

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return wrapper