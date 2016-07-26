import datadog

import logging


LOG_LEVEL_ALERT_TYPE_MAPPINGS = {
    logging.DEBUG: "info",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "error"
}


class DatadogLogHandler(logging.Handler):
    def __init__(self, tags=None, mentions=None, **kwargs):
        super(DatadogLogHandler, self).__init__(**kwargs)

        self.tags = tags
        self.mentions = mentions

    def emit(self, record):
        text = self.format(record)

        if self.mentions is not None:
            text = "\n\n".join([text, " ".join(self.mentions)])

        create_args = {
            "title": record.getMessage(),
            "text": text
        }

        if self.tags is not None:
            create_args["tags"] = self.tags

        if record.levelno in LOG_LEVEL_ALERT_TYPE_MAPPINGS:
            create_args["alert_type"] = LOG_LEVEL_ALERT_TYPE_MAPPINGS[record.levelno]

        datadog.api.Event.create(**create_args)
