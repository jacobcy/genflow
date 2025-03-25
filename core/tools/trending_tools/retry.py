"""重试机制工具

提供接口重试等功能。
"""
import logging
import functools
from typing import Callable, TypeVar, Any
from time import sleep

logger = logging.getLogger(__name__)

T = TypeVar('T')

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """接口重试装饰器

    Args:
        max_retries: 最大重试次数，默认3次
        delay: 初始重试延迟(秒)，默认1秒
        backoff: 重试延迟倍数，默认2倍
        exceptions: 需要重试的异常类型

    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if retry < max_retries - 1:
                        logger.warning(
                            f"接口调用失败 ({func.__name__}), 正在进行第{retry + 1}次重试: {str(e)}"
                        )
                        sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"接口调用失败 ({func.__name__}), 已达到最大重试次数{max_retries}: {str(e)}"
                        )

            # 所有重试都失败后，返回空列表（适用于话题抓取场景）
            logger.error(f"跳过失败的接口调用: {func.__name__}")
            return []

        return wrapper
    return decorator
