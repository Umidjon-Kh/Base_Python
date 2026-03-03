from sys import stderr
from loguru import logger
from typing import Any, Dict


class LogManager:
    """
    Manager of Logging that uses Loguru
    Can be Custmozed:
    1) Set logs default min stream level
    2) Set logs default min write level
    3) Choose write logs or not
    4) Choose style of logs format
    5) Can add your own styles for file handler and console hanlder
    """

    __slots__ = '__config'

    def __init__(self, config: Dict[str, Any]) -> None:
        self.__config = config
        self.configure()

    def configure(self) -> None:
        """Sets configurations for loguru logger"""
        # 1.Action: Removing all old handlers
        logger.remove()

        # 2.Action: Configuring console handler if enabled
        console_cfg = self.__config.get('console', {})
        if console_cfg.get('enabled', True):
            self._setup_console(console_cfg)

        # 3.Action: Configuring file handler if enabled
        file_cfg = self.__config.get('file', {})
        if file_cfg.get('enabled', False):
            self._setup_file(file_cfg)

        # 4.Action: If not added handlers config att all, adds only stream logger
        if not logger._core.handlers:  # type: ignore
            self._setup_console({})

    def _setup_console(self, cfg: Dict[str, Any]) -> None:
        """Configuring and setting all params to stream handler"""
        # Log params
        level = cfg.get('level', 'debug').upper()
        # Style params
        style = cfg.get('style', 'simple')
        styles_data = self.__config.get('styles_data', {})
        styles = styles_data.get('console', {})
        style_to_use = styles.get(style, "{time:HH:mm:ss} | {message}")
        colorize = cfg.get('colorize', True)
        logger.add(stderr, format=style_to_use, level=level, colorize=colorize)

    def _setup_file(self, cfg: Dict[str, Any]) -> None:
        """Configuring and setting all params to file handler"""
        # Log params
        level = cfg.get('level', 'debug')
        rotation = cfg.get('rotation', None)
        retention = cfg.get('retention', None)
        compression = cfg.get('compression', None)
        # Style format of logs
        style = cfg.get('style', 'simple')
        style_to_use = self.__config.get('styles_data', {}).get('file', {}).get(style, "{time:HH:mm:ss} | {message}")

        logger.add(
            cfg.get('path', 'app.log'),
            format=style_to_use,
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
        )
