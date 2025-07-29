from assertpy import assert_that

from threelog.logger_implementations.console_logger import ConsoleLogger
from threelog.logger_implementations.null_logger import NullLogger
from threelog.three_logger import ThreeLog

DEFAULT_LOGGER_NAME = type(NullLogger()).__name__


def test_uses_null_logger_by_default():
    assert_that(ThreeLog.logger_type()).is_equal_to(DEFAULT_LOGGER_NAME)


def test_can_log_debug_message_when_uninitialized():
    ThreeLog.debug("test")


def test_can_log_info_message_when_uninitialized():
    ThreeLog.info("test")


def test_can_log_warn_message_when_uninitialized():
    ThreeLog.warn("test")


def test_can_log_error_message_when_uninitialized():
    ThreeLog.error("test")


def test_cannot_unset_logger():
    ThreeLog.initialize(None)
    assert_that(ThreeLog.logger_type()).is_equal_to(DEFAULT_LOGGER_NAME)


def test_cannot_set_invalid_logger():
    class NotALoggingImplementation:
        pass

    ThreeLog.initialize(NotALoggingImplementation())
    assert_that(ThreeLog.logger_type()).is_equal_to(DEFAULT_LOGGER_NAME)


def test_can_set_valid_logger():
    ThreeLog.initialize(ConsoleLogger())
    assert_that(ThreeLog.logger_type()).is_equal_to(type(ConsoleLogger()).__name__)
