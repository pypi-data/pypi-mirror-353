import sys
from typing import Literal, Sequence, Union

from loguru import logger

SinkType = Literal["stdout", "file"]


def configure_logger(
    *,
    log_file_name: str | None = None,
    sink: Union[SinkType, Sequence[SinkType]],
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
):
    logger.remove()
    format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}.{function}:{line}</cyan> - <level>{message}</level>"

    sinks = [sink] if isinstance(sink, str) else sink

    for s in sinks:
        if s == "stdout":
            logger.add(
                sys.stdout,
                format=format,
                level=level,
                enqueue=True,
                backtrace=True,
                diagnose=True,
                colorize=True,
            )
        elif s == "file":
            logger.add(
                log_file_name,
                rotation="100MB",
                format=format,
                level=level,
                enqueue=True,
                backtrace=True,
                diagnose=True,
                serialize=True,
            )


configure_logger(log_file_name="app.log", sink="stdout")
