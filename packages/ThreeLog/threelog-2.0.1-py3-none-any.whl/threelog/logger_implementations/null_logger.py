from ..logger_implementation import LoggerImplementation


class NullLogger(LoggerImplementation):
    """
    This logger is used as the default logger implementation if no other logger is initialized.

    Log messages are discarded.

    There may be valid use-cases for this logger in production, but it's primary purpose to
    avoid null pointer exceptions in the StriveLogger.
    """

    def debug(self, message: str, trace_id: str | None, extra: dict | None = None) -> None:
        pass

    def info(self, message: str, trace_id: str | None, extra: dict | None = None) -> None:
        pass

    def warn(self, message: str, trace_id: str | None, extra: dict | None = None) -> None:
        pass

    def error(
        self,
        message: str,
        trace_id: str | None,
        exc_info: BaseException | str | None = None,
        extra: dict | None = None,
    ) -> None:
        pass
