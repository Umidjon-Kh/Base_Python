from sys import stderr
from loguru import logger
from typing import Any, Dict, Optional

# Project modules
from ..tools import ConfigNormalizer, Loader


class LogManager:
    """
    Configurator for Loguru to customize logs
    1) Set logs default min stream level
    2) Set logs default min write level
    3) Choose write logs or not
    4) Choose format of logs stderr to output
    5) Choose colors of logs msg and etc..
    """

    __slots__ = ('__config', '__style_loader')

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        # if config got in Path type
        self.__config = ConfigNormalizer().data_normalizer(data=config or {}, mg='log_mg')
        self.__style_loader = Loader()

    # Main log configurator that calls other methdos
    def configure(self) -> None:
        """Sets configuration for Loguru"""
        # 1.Action: Deleting all old LoguruHandlers
        logger.remove()

        # 2.Action: Configuring console if enabled
        console_cfg = self.__config.get('console', {})
        if console_cfg.get('enabled', True):
            self._setup_console(console_cfg)

        # 3.Action: Configuring file if enabled
        file_cfg = self.__config.get('file', {})
        if file_cfg.get('enabled', True):
            self._setup_file(file_cfg)

        # 4.Action: If not added handlers config att all, adds only stream logger
        if not logger._core.handlers:  # type: ignore
            self._setup_console({'enabled': True})

    # Stream logger
    def _setup_console(self, cfg: Dict[str, Any]) -> None:
        """Settings stream to console"""
        # Log params
        level = cfg.get('level', 'debug').upper()
        colorize = cfg.get('colorize', True)
        # Style format of logs
        style = cfg.get('style', None)
        styles_data = cfg.get('styles_data', None)
        styles_path = cfg.get('styles_path', None)
        # Getting style from style_data or style_path
        style_to_use = self.get_style('console', style, styles_data, styles_path)

        logger.add(stderr, format=style_to_use, level=level, colorize=colorize)  # type: ignore

    # File logger
    def _setup_file(self, cfg: Dict[str, Any]) -> None:
        """Settings file logger"""
        # Log params
        level = cfg.get('level', 'debug').upper()
        # Style format of logs
        style = cfg.get('style', None)
        styles_data = cfg.get('styles_data', None)
        styles_path = cfg.get('styles_path', None)
        # Getting style from style_data or stye_path
        style_to_use = self.get_style('file', style, styles_data, styles_path)

        rotation = cfg.get('rotation', None)
        retention = cfg.get('retention', None)
        compression = cfg.get('compression', None)

        logger.add(
            cfg['path'],
            format=style_to_use,  # type: ignore
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
        )

    def get_style(
        self, handler: str, style: Optional[str] = None, data: Optional[Dict] = None, path: Optional[str] = None
    ) -> Optional[str]:
        """
        Returns string of format and handler style
        If styles_data is not None, gets from it else loads from file
        """
        if data is None:
            data = self.__style_loader.load_from_file('styles', path)
        handler_styles = data.get(handler, {})
        return handler_styles.get(style) or handler_styles.get('simple')
