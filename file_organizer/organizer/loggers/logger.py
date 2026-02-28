import json
from sys import stderr
from loguru import logger
from typing import Any, Dict, Optional
from pathlib import Path

# Project modules
from ..src import PathError, ConfigError


class LogConfigurer:
    """
    Configurator for Loguru to customize logs
    1) Set logs default min stream level
    2) Set logs default min write level
    3) Choose write logs or not
    4) Choose format of logs stderr to output
    5) Choose colors of logs msg and etc..
    """

    DEFAULT_STYLES_PATH = Path(__file__).parent.parent / 'configs' / 'default_styles.json'

    __slots__ = ('__config',)

    def __init__(self, config: Optional[Dict[str, Any]] | Path) -> None:
        # if config got in Path type
        if isinstance(config, (str, Path)):
            self.__config = self._load_from_file(config)
        else:
            self.__config = config or {}

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
        # Default styles path
        def_path = self.DEFAULT_STYLES_PATH
        # Log params
        level = cfg.get('level', 'debug').upper()
        # Style format of logs
        style = cfg.get('style', None)
        # Style data priority is always higher than style path
        styles_data = cfg.get('styles_data', None)
        styles_path = cfg.get('styles_path', None)

        # Getting style from style_data
        style_to_use = styles_data.get(style, None) if styles_data else None
        if style_to_use is None:
            styles_data = self._load_from_file(def_path, styles_path)
            style_to_use = self._select_style(style, styles_data, 'console', def_path)

        colorize = cfg.get('colorize', True)

        logger.add(stderr, format=style_to_use, level=level, colorize=colorize)  # type: ignore

    # File logger
    def _setup_file(self, cfg: Dict[str, Any]) -> None:
        """Settings file logger"""
        # Default styles path
        def_path = self.DEFAULT_STYLES_PATH
        # Log params
        level = cfg.get('level', 'debug').upper()
        # Style format of logs
        style = cfg.get('style', None)
        # Style data priority is always higher than style path
        styles_data = cfg.get('styles_data', None)
        styles_path = cfg.get('styles_path', None)

        # Getting style from style_data
        style_to_use = styles_data.get(style, None) if styles_data else None
        if style_to_use is None:
            styles_data = self._load_from_file(def_path, styles_path)
            style_to_use = self._select_style(style, styles_data, 'file', def_path)

        log_file = cfg.get('path')
        if not log_file:
            raise ConfigError('File logger enabled but no \'path\' specified')

        rotation = cfg.get('rotation', None)
        retention = cfg.get('retention', None)
        compression = cfg.get('compression', None)

        logger.add(
            log_file,
            format=style_to_use,  # type: ignore
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
        )

    def _load_from_file(self, def_path: Path, path: Optional[Path] = None) -> Dict:
        """Loads all style formats from path"""
        try:
            # If path is not None and exits we use it, else use default_path
            if path and (p := Path(path).resolve()).exists():
                path_to_use = p
            else:
                path_to_use = def_path

            with open(path_to_use, encoding='utf-8') as file:
                return json.load(file)
        except (IOError, json.JSONDecodeError) as exc:
            raise PathError(f'Error while loading data: {exc}')

    def _select_style(self, style: Optional[str], styles: Optional[Dict], handler: str, path: Path) -> Optional[str]:
        """
        Return format string for the given style name.
        If not found, try 'simple', else None.
        """
        if styles is None:
            styles = self._load_from_file(def_path=path)
        handler_styles = styles.get(handler, {})
        return handler_styles.get(style) or handler_styles.get('simple')
