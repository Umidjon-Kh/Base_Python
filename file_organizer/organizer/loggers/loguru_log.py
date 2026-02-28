import logging
from sys import stderr
from loguru import logger
from typing import Optional


# class to Handle logs from logging
class InterceptHandler(logging.Handler):
    """
    Handler for standard module Logging.
    Handls all messages from logging and
    converts it to Loguru logs, after sends it
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Triggers every time, when from logging sends message
        :param record: Objects of LogRecord that contains all info
        """
        # 1.Action: Getting level of log for Loguru
        # record.levelname its a string with level of log like 'DEBUG' or 'INFO'
        try:
            # trying to get level from name of log
            level = logger.level(record.levelname).name
        except ValueError:
            # if raises Error try to get level in digits
            level = record.levelno

        # 2.Acction: Finding out where we get this message
        # Using depth cause all logs we got in wrapped format
        # To reach max log depth we use digit 6
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


# main logger of Loguru
def loguru_logger(
    stream_level: str = 'debug', log_file: Optional[str] = None, write_level: str = 'debug'
) -> logging.Logger:
    """
    Customizes Loguru for output to console (stderr) and optional for file
    Handles all logs from logging and send it from Loguru

    :param stream_level: min level fro stream_handler (console output)
    :param log_file: path to save logs
    :param write_level: min level to write logs to log file
    :return: logger with name 'organizer' from standard logging
    """

    # 1.Action: Removing all old loggers to not dublicate logs msg
    # It needed to delete LoguruHandler cause we do it by self
    logger.remove()

    # 2.Action: Customizing logger to stream
    console_format = (
        '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
        '<cyan><level>{level: <8}</level></cyan> | '
        '<yellow>{name}</yellow>:<blue>{function}</blue>:<blue>{line}</blue> | '
        '<level>{message}</level>'
    )
    logger.add(stderr, format=console_format, level=stream_level.upper(), colorize=True)  # thread of output

    # 3.Action: if got path to save file
    if log_file:
        file_format = '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}'
        logger.add(
            log_file,
            format=file_format,
            level=write_level.upper(),
            rotation='10 MB',
            retention='10 days',
            compression='zip',
        )

    # 4.Action: Setting our handler
    # instead of logging standard handlers
    # first of all we need to delete old root handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Adding our handler
    logging.root.addHandler(InterceptHandler())

    # Setting level to root handler
    # All filtrations gets from heam to stream and write
    logging.root.setLevel(logging.DEBUG)

    # Returning our logger 'organizer'
    return logging.getLogger('organizer')
