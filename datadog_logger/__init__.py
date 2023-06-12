from collections.abc import Iterable
from datadog_logger.handler import DatadogLogHandler
import logging
from typing import Optional


def log_error_events(
    name: Optional[str] = None,
    tags: Optional[list[str]] = None,
    mentions: Optional[Iterable[str]] = None
) -> None:
    handler = DatadogLogHandler(tags=tags, mentions=mentions, level=logging.ERROR)
    logging.getLogger(name).addHandler(handler)
