from datadog_logger.handler import DatadogLogHandler
import logging


def log_error_events(name=None, tags=None, mentions=None):
    handler = DatadogLogHandler(tags=tags, mentions=mentions, level=logging.ERROR)
    logging.getLogger(name).addHandler(handler)
