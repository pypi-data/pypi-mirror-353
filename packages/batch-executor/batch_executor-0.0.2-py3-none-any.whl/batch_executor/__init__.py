"""Top-level package for batch_executor."""

__author__ = """Rex Wang"""
__email__ = '1073853456@qq.com'
__version__ = '0.0.2'

from .logger_config import setup_logger
from .main import (
    Executor, batch_executor,
    batch_async_executor, batch_hybrid_executor,
    batch_process_executor, batch_thread_executor
)
    