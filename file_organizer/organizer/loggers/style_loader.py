# loggers/style_loader.py
import json
from pathlib import Path
from typing import Dict, Optional

# Project modules
from ..src import PathError


class StyleLoader:
    """Loads styles for logs and returns it to LogConfigure"""

    # default styles path for logs
    DEFAULT_STYLES_PATH = Path(__file__).parent.parent / 'configs' / 'default_styles.json'

    __slots__ = ('default_styles_path', '_styles_cache')

    def __init__(self, default_styles_path: Optional[str] = None):
        if default_styles_path and (p := Path(default_styles_path).resolve()).exists():
            self.default_styles_path = p
        else:
            self.default_styles_path = self.DEFAULT_STYLES_PATH
        self._styles_cache: Dict = {}

    def load_styles(self, custom_path: Optional[str] = None) -> Dict:
        """Loads style from file (Custom or Default)"""
        # Checking custom path is not None and exist or not
        if custom_path and (p := Path(custom_path).resolve()).exists():
            path = p
        else:
            path = self.default_styles_path
        # If we cached styles we return it
        if self._styles_cache:
            return self._styles_cache
        try:
            with open(path, encoding='utf-8') as file:
                self._styles_cache = json.load(file)
            return self._styles_cache
        except (IOError, json.JSONDecodeError) as exc:
            raise PathError(f"Failed to load styles: {exc}")

    def get_style(
        self,
        handler: str,
        style_name: Optional[str] = None,
        styles_data: Optional[Dict] = None,
        custom_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Returns string of format and handler style
        If styles_data is not None, gets from it else loads from file
        """
        if styles_data is None:
            styles_data = self.load_styles(custom_path)
        handler_styles = styles_data.get(handler, {})
        return handler_styles.get(style_name) or handler_styles.get('simple')
