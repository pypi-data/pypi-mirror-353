from assertpy import assert_that

from threelog import StriveLogger
from threelog.logger_implementations.null_logger import NullLogger

DEFAULT_LOGGER_NAME = type(NullLogger()).__name__


def test_can_log_debug_message_with_alias():
    StriveLogger.debug("test")


def test_can_log_info_message_with_alias():
    StriveLogger.info("test")


def test_can_log_warn_message_with_alias():
    StriveLogger.warn("test")


def test_can_log_error_message_with_alias():
    StriveLogger.error("test")
