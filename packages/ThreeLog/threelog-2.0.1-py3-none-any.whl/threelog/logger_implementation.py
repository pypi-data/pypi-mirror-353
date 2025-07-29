from abc import ABC, abstractmethod


class LoggerImplementation(ABC):
    @abstractmethod
    def debug(
        self,
        message: str,
        trace_id: str | None,
        extra: dict | None = None,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def info(
        self,
        message: str,
        trace_id: str | None,
        extra: dict | None = None,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def warn(
        self,
        message: str,
        trace_id: str | None,
        extra: dict | None = None,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def error(
        self,
        message: str,
        trace_id: str | None,
        exc_info: BaseException | str | None = None,
        extra: dict | None = None,
    ) -> None:
        raise NotImplementedError()
