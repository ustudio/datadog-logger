import logging
import sys
import traceback
from types import TracebackType
from typing import Tuple, Type, Union
from unittest import mock, TestCase

from datadog_logger.handler import DatadogLogHandler
from datadog_logger import log_error_events


def make_exc_info(
) -> Union[Tuple[Type[BaseException], BaseException, TracebackType], Tuple[None, None, None]]:
    try:
        raise RuntimeError("message")
    except Exception:
        return sys.exc_info()


class TestDatadogLogger(TestCase):
    def tearDown(self) -> None:
        super().tearDown()

        # This tries to clean up the root logger if it was configured
        # via log_error_events. Logger.handlers is an undocumented
        # implementation detail of the Logger class, but there is no
        # other way to remove a handler other than having the instance
        # you want to remove, and there is no way to "reset" the
        # logging library
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if handler.__class__ is DatadogLogHandler:
                root_logger.removeHandler(handler)

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_logs_to_datadog(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message"
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(title="Some message", text="Some message")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_logs_formatted_message_as_text(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        exc_info = make_exc_info()

        record = logging.makeLogRecord({
            "msg": "Some message",
            "exc_info": exc_info
        })

        expected_text = "\n".join(
            ["Some message", "".join(traceback.format_exception(*exc_info))]).rstrip("\n")

        handler.emit(record)

        mock_event_class.create.assert_called_with(title="Some message", text=expected_text)

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_tags_from_constructor(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler(tags=["some:tag"])

        record = logging.makeLogRecord({
            "msg": "Some message"
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message",
            tags=["some:tag"])

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_mentions_from_constructor(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler(mentions=["@mention-1", "@mention-2"])

        record = logging.makeLogRecord({
            "msg": "Some message"
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message\n\n@mention-1 @mention-2")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_maps_debug_to_info(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message",
            "levelno": logging.DEBUG
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message",
            alert_type="info")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_maps_info_to_info(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message",
            "levelno": logging.INFO
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message",
            alert_type="info")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_maps_warning_to_warning(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message",
            "levelno": logging.WARNING
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message",
            alert_type="warning")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_maps_error_to_error(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message",
            "levelno": logging.ERROR
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message",
            alert_type="error")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_includes_maps_critical_to_error(self, mock_event_class: mock.Mock) -> None:
        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message",
            "levelno": logging.CRITICAL
        })

        handler.emit(record)

        mock_event_class.create.assert_called_with(
            title="Some message", text="Some message",
            alert_type="error")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_log_error_registers_error_reporter_with_configuration(
        self,
        mock_event_class: mock.Mock
    ) -> None:
        log_error_events(tags=["some:tag"], mentions=["@mention"])

        logging.info("Should not be logged")
        logging.error("Should be logged")

        mock_event_class.create.assert_called_once_with(
            title="Should be logged", text="Should be logged\n\n@mention",
            tags=["some:tag"], alert_type="error")

    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_log_error_registers_error_reporter_with_configuration_on_logger(
        self,
        mock_event_class: mock.Mock
    ) -> None:
        some_logger = logging.getLogger("some.logger")
        other_logger = logging.getLogger("other.logger")

        log_error_events("some.logger", tags=["some:tag"], mentions=["@mention"])

        some_logger.info("Should not be logged")
        some_logger.error("Should be logged")

        other_logger.error("Should not be logged")

        mock_event_class.create.assert_called_once_with(
            title="Should be logged", text="Should be logged\n\n@mention",
            tags=["some:tag"], alert_type="error")

    @mock.patch("logging.Handler.handleError", autospec=True)
    @mock.patch("datadog_logger.handler.Event", autospec=True)
    def test_emit_calls_handle_error_when_it_raises_an_exception(
        self,
        mock_event_class: mock.Mock,
        mock_handle_error: mock.Mock
    ) -> None:
        mock_event_class.create.side_effect = Exception("event create error")

        handler = DatadogLogHandler()

        record = logging.makeLogRecord({
            "msg": "Some message"
        })

        handler.emit(record)

        mock_handle_error.assert_called_once_with(handler, record)
