# DataDog Logger #

Note: This library does not send logs to Datadog's Log Management product. See
Datadog's documentation for how to configure log collection. See
https://docs.datadoghq.com/logs/log_collection/

A Python `logging.Handler` for sending log messages to DataDog as Events in
the Events Explorer.

## Installation ##

```
pip install datadog-logger
```

## Usage ##

The simplest way to enable logging to DataDog is to use the
`log_error_events` helper, which will cause all `logging.ERROR` and
higher messages to be sent to DataDog:

```python
import datadog
from datadog_logger import log_error_events
import logging

# Authenticate with DataDog
datadog.initialize(api_key="api-key", app_key="app-key")

# Note, a normal STDOUT handler will not be configured if this is not
# called first
logging.basicConfig()

log_error_events(tags=["tag1:value", "tag2:value"], mentions=["@devs", "@slack"])

logging.error("Oh no!")
```

This will enable the handler on the root logger; `tags` and `mentions`
may both be `None`, in which case none will be included. The handler
will have a log level of `logging.ERROR`, meaning only `ERROR` and
`CRITICAL` (or any higher custom levels) will be sent to DataDog.

A specific logger may also be specified by name:

```python
log_error_events("some.logger")
```

### Details ###

The `Handler` may also be created and added to a logger manually:

```python
import datadog
from datadog_logger import DatadogLogHandler
import logging

datadog.initialize(api_key="api-key", app_key="app-key")

datadog_handler = DatadogLogHandler(
    tags=["some:tag"], mentions=["@some-mention"], level=logging.WARNING)

# Enable STDOUT logging
logging.basicConfig()

# The root logger
logger = logging.getLogger()
logger.addHandler(datadog_handler)

# This will be logged, because the level is WARNING
logger.warning("Watch out!")

# This will not
logger.info("Lets not log everything to DataDog")
```

When the event is created, the `msg` of the log record will be passed
as the title of the event. Normally, this would be the string passed
into the logging call, with any `%` substitutions applied.

The text of the event will be the formatted record. If the log
record includes `exc_info` (i.e. because you called
`logging.exception`, or passed `exc_info` to the log function), then
the full stack trace will be included in the event text.

Any `@mentions` passed via the `mentions` constructor argument will be
appended to the end of the text, so this library can be used to alert,
via DataDog, on particular log messages.
