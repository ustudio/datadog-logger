from collections.abc import Iterable
from datadog.api.events import Event
from datadog.api.exceptions import ApiError
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

            response = Event.create(**create_args)  # type: ignore[arg-type]

            # The datadog client is muted by default, which means it logs
            # errors returned by the API and returns them to the caller
            # instead of raising them, so failures to submit the event have
            # to be detected here to be reported by handleError
            if isinstance(response, dict) and response.get("errors"):
                raise ApiError(response)

        except Exception:
            self.handleError(record)
