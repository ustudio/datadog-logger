import datadog

import logging


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

        datadog.api.Event.create(**create_args)
