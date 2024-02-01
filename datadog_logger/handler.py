from collections.abc import Iterable
from datadog.api.events import Event
import logging
from typing import Any, Optional


LOG_LEVEL_ALERT_TYPE_MAPPINGS = {
    logging.DEBUG: "info",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "error"
}


class DatadogLogHandler(logging.Handler):
    def __init__(
        self,
        tags: Optional[list[str]] = None,
        mentions: Optional[Iterable[str]] = None,
        **kwargs: Any
    ):
        super(DatadogLogHandler, self).__init__(**kwargs)

        self.tags = tags
        self.mentions = mentions

    def emit(self, record: logging.LogRecord) -> None:
        try:
            text = self.format(record)

            if self.mentions is not None:
                text = "\n\n".join([text, " ".join(self.mentions)])

            create_args: dict[str, object] = {
                "title": record.getMessage(),
                "text": text
            }

            if self.tags is not None:
                create_args["tags"] = self.tags

            if record.levelno in LOG_LEVEL_ALERT_TYPE_MAPPINGS:
                create_args["alert_type"] = LOG_LEVEL_ALERT_TYPE_MAPPINGS[record.levelno]

            Event.create(**create_args)  # type: ignore[no-untyped-call]

        except Exception:
            self.handleError(record)
