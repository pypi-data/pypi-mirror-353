import time
from datetime import timedelta
from typing import Callable, Any
import asyncio


def time_checker_base(title: str, notifier: Callable[[str], bool | None] | None, func: Callable[..., Any], is_async: bool):
    async def async_exec(*args, **kwargs):
        return await func(*args, **kwargs)

    def sync_exec(*args, **kwargs):
        return func(*args, **kwargs)

    def wrapper(*args, **kwargs):
        if notifier is None:
            print(f'{title} 시작')
        else:
            notifier(f'{title} 시작')

        start = time.time()

        if is_async:
            result = asyncio.ensure_future(async_exec(*args, **kwargs))  # 코루틴을 올바르게 실행
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(result)
        else:
            result = sync_exec(*args, **kwargs)

        delta_seconds = time.time() - start
        end = timedelta(seconds=delta_seconds)

        if notifier is None:
            print(f'{title} 종료({end})')
        else:
            notifier(f'{title} 종료({end})')

        return result

    return wrapper


def time_checker(title: str, notifier: Callable[[str], bool | None] | None = None):
    def decorator(func: Callable[..., Any]):
        return time_checker_base(title, notifier, func, is_async=False)

    return decorator


def async_time_checker(title: str, notifier: Callable[[str], bool | None] | None = None):
    def decorator(func: Callable[..., Any]):
        return time_checker_base(title, notifier, func, is_async=True)

    return decorator
