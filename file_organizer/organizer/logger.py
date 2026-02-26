import logging
from sys import stdout
from typing import Optional


def setup_logger(
    verbose: bool = False,
    stream_level: str = 'debug',
    log_file: Optional[str] = None,
    write_level: str = 'debug',
) -> logging.Logger:
    """
    Customize logger: output to xonsole and optianal to file
    Can set level for output or write to file

    param: verbose: Shows logs
    param: stream_level: Level to output (default=Debug)
    param: log_file: Writes logs to file
    param: write_level: Level to write into file (default=Debug)
    """

    # Getting logger of object
    logger = logging.getLogger('file_organizer')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Format of logs
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # ------------ Handling for console -----------
    console_handler = logging.StreamHandler(stdout)
    # Setting level and format
    console_handler.setLevel(getattr(logging, stream_level.upper(), logging.DEBUG))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ------------ Handling for file -----------
    if log_file:
        file_handlar = logging.FileHandler(log_file, encoding='utf-8')
        # Setting level and format
        file_handlar.setLevel(getattr(logging, write_level.upper(), logging.DEBUG))
        file_handlar.setFormatter(formatter)
        logger.addHandler(file_handlar)

    return logger
