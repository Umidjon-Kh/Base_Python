import logging
from rich.logging import RichHandler
from rich.console import Console
from typing import Optional


# Main logger for rich logging mode
def rich_logger(
    stream_level: str = 'debug', log_file: Optional[str] = None, write_level: str = 'debug'
) -> logging.Logger:
    """
    Handls all logs and wraps logs to rich logger msg
    To show in console (StreamHandler)

    :param stream_level: Level showing in console
    :param log_file: Path of file to save logs
    :param write_level: Level to write logs in to file
    """

    # 1.Action: Creating root logger (or getting existed)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 2.Action: Removing all old handlers to not dublicate
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 3.Action: Creating console Rich
    console = Console()

    # 4.Action: Creating RichHandler for connecting to logger
    rich_handler = RichHandler(
        console=console,  # Console to stream
        rich_tracebacks=True,  # Fancy tracebacks
        tracebacks_show_locals=True,  # Shows local variables when error
        markup=True,  # Acces markup rich, e.g.:[bold]
        show_time=True,  # show time
        show_level=True,  # show level
        show_path=False,
        level=getattr(logging, stream_level.upper()),
    )
    root_logger.addHandler(rich_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf_8')
        file_handler.setLevel(getattr(logging, write_level.upper()))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 6.Action: Returning logger
    return logging.getLogger('organizer')
