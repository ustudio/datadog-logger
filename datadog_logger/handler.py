import datadog

import logging


class DatadogLogHandler(logging.Handler):
    def emit(self, record):
        datadog.api.Event.create(
            title=record.getMessage(), text=self.format(record))
