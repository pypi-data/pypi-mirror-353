This project is a renamed and maintained fork of [Strive Logger](https://github.com/strivesolutions/strive-logger-py), originally developed by Strive Business Solutions. It is now maintained by Third Version Technology Ltd under the MIT License.

[Migration Guide from Strive Logger to Three Log](migration_from_strive_logger.md)

<p align="center">
<img src="https://avatars.githubusercontent.com/u/124225064?s=200&v=4" alt="Third Version Technology Logo" />
</p>

# Three Log

[![Continuous Integration](https://github.com/thirdversion/threelog-py/actions/workflows/ci.yml/badge.svg)](https://github.com/thirdversion/threelog-py/actions/workflows/ci.yml)

## What is Three Log?

Three Log is a logging abstraction layer which is used in our previous company's python projects, but was abandoned when we moved to a new company. We have decided to continue using it in our new projects, and have renamed it to "Three Log" to avoid confusion with the original Strive Logger.

We find that it works well for us, perhaps it will also work for you.

## How does it work?

The package provides a class named "ThreeLog" which has class methods for "debug", "info", "warn" and "error" level logging. A dictionary of extra information to be logged can optionally be supplied to all methods, and an exception or error string can also optionally be provided to the error method.

## Where does it log?

The actual logging is handled by a logger implementation which must be supplied once during your application startup, by calling the "initialize" method.

```
from threelog import ThreeLog, ConsoleLogger


ThreeLog.initialize(logger=ConsoleLogger())
```

### Logger Implementations

You may choose to create your own logger implementation, for example to wrap up a structured logger like Google's StackDriver, but some simple implementations have been provided as part of this project as well.

To create your own implementation, create a class which inherits from LoggerImplementation and implement the required methods:

```
from threelog.logger_implementation import LoggerImplementation

class MyLogger(LoggerImplementation):
    def debug(self, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        # TODO: log somewhere
        pass

    def info(cls, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        # TODO: log somewhere
        pass

    def warn(cls, message: str, trace_id: Optional[str], extra: Dict = None) -> None:
        # TODO: log somewhere
        pass

    def error(
        cls,
        message: str,
        trace_id: Optional[str],
        exc_info: Optional[Union[BaseException, str]],
        extra: Optional[Dict],
    ) -> None:
        # TODO: log somewhere
        pass
```

#### Provided Implementations

##### ConsoleLogger

`from threelog.logger_implementations.console_logger import ConsoleLogger`

Prints all log messages to the console.

##### NullLogger

`from threelog.logger_implementations.null_logger import NullLogger`

Throws away all log requests. This implementation is used prior to initialization in order to ensure that ThreeLog doesn't throw null pointer exceptions if not initialized.

##### PythonLogger

`from threelog.logger_implementations.python_logger import PythonLogger`

Wraps an instance of a python logger. You can supply a name in order to create or use an existing instance, or simply use the root logger. This logger can log simple strings, or it can log as JSON.

##### UvicornLogger

`from threelog.logger_implementations.uvicorn_logger import UvicornLogger`

A specialized implementation of the PythonLogger - this logger will attach to the python logger instance which uvicorn creates. If JSON logging is enabled, this logger will also attach and reformat uvicorn.access logging calls.

Useful if using ThreeLog in a FastAPI project.

## Tracing

ThreeLog can also supply trace ids to log entries, if a TracerImplementation is supplied during initialization.

No tracer implementations are included in this library currently - you may implement your own by inheriting from TracerImplementation and implementing the "get_trace_id" method:

```
from threelog.tracer_implementation import TracerImplementation


class MyTracerImplementation(TracerImplementation):
    def get_trace_id(self) -> str:
        # TODO: find or set a trace ID and return it
        raise NotImplementedError()
```

## Example usage

```
from threelog import ThreeLog, UvicornLogger


ThreeLog.initialize(logger=UvicornLogger(level="DEBUG", enable_json=True))
ThreeLog.info("Logging initialized", extra={"timestamp": datetime.now().isoformat()})
```

## Contributing

This is an open source project, and thus contributions to this project are welcome - please feel free to [create a new issue](/issues/new/choose) if you encounter any problems, or [submit a pull request](/pulls).

If submitting a pull request, please ensure the following standards are met:

1. Code files must be formatted (run ./lint.sh prior to submitting)

2. Tests must pass (run ./test.sh). New test cases to validate your changes are highly recommended.

3. Implementations must not add any project dependencies. If you wish to create a logger or tracer implementation which depends on another package, consider creating a new library which references this one, and submitting a PR which documents your new implementation here.

## Additional information

This package has no dependencies on any other packages.
