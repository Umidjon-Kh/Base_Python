from abc import ABC
from typing import Dict, Any, Optional


class LevelStyle(ABC):
    """
    Abstract base class for log level styling.

    Each concrete level style (e.g., DebugStyle, InfoStyle) defines which
    components (icon, level name, message, time, path, function, line)
    are displayed, their colors, and the overall format for console and file
    handlers.

    All configuration is passed as a dictionary (typically loaded from JSON).
    Missing keys are filled with sensible defaults.

    The style produces a format string compatible with loguru, using loguru's
    placeholders like {time}, {level.name}, {message}, {file.path}, {function}, {line}
    and color tags like <red>, </red>.
    """

    __slots__ = (
        '_show_icon',
        '_show_level_str',
        '_level_icon',
        '_level_str',
        '_level_color',
        '_show_msg',
        '_msg_color',
        '_show_time',
        '_time_format',
        '_time_color',
        '_show_path',
        '_path_color',
        '_show_function',
        '_function_color',
        '_show_line',
        '_line_color',
        '_console_style',
        '_file_style',
    )

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the style from a configuration dictionary.

        Args:
            config: Dictionary with keys corresponding to the attributes.
                    Special key 'styles' may contain nested 'console' and 'file'
                    format strings, which are extracted into _console_style
                    and _file_style.
        """
        # Default values for all attributes
        defaults: Dict[str, Any] = {
            'show_icon': False,
            'show_level_str': True,
            'level_icon': None,
            'level_str': None,  # None means use default level name
            'level_color': 'white',
            'show_msg': True,
            'msg_color': 'white',
            'show_time': True,
            'time_format': '%H:%M:%S',
            'time_color': None,
            'show_path': False,
            'path_color': None,
            'show_function': False,
            'function_color': None,
            'show_line': False,
            'line_color': None,
            'console_style': '| level | msg | time',
            'file_style': '| level | msg | time',
        }

        # Extract nested 'styles' if present
        if 'styles' in config and isinstance(config['styles'], dict):
            styles_dict = config.pop('styles')
            if 'console' in styles_dict:
                config['console_style'] = styles_dict['console']
            if 'file' in styles_dict:
                config['file_style'] = styles_dict['file']

        # Set each slot from config or default
        for slot in LevelStyle.__slots__:
            attr_name = slot.removeprefix('_')  # remove leading underscore
            value = config.get(attr_name, defaults.get(attr_name))
            object.__setattr__(self, slot, value)

    # ----------------------------------------------------------------------
    # Helper methods
    # ----------------------------------------------------------------------

    @staticmethod
    def _colored_format(text: str, color: Optional[str]) -> str:
        """Wrap text with color tag if color is specified."""
        if color and text:
            return f'<{color}>{text}</{color}>'
        return text

    # ----------------------------------------------------------------------
    # Properties that return format fragments (with loguru placeholders and colors)
    # ----------------------------------------------------------------------

    @property
    def level(self) -> str:
        """
        Return the format fragment for the log level.
        Includes icon and level name according to settings, with optional color.
        Uses loguru placeholders: {level.icon}, {level.name}
        """
        parts = []
        if self._show_icon and self._level_icon:
            parts.append(self._level_icon)
        if self._show_level_str:
            level_text = self._level_str if self._level_str else '{level.name}'
            level_text = self._colored_format(level_text, self._level_color)
            parts.append(level_text)
        result = ' '.join(parts)
        return result

    @property
    def msg(self) -> str:
        """Return the format fragment for the message, with optional color."""
        if self._show_msg:
            return self._colored_format('{message}', self._msg_color)
        return ''

    @property
    def time(self) -> str:
        """
        Return the format fragment for the time, using the configured time format and color.
        Example: <blue>{time:HH:mm:ss}</blue>
        """
        if self._show_time:
            time = f'{{time:{self._time_format}}}'
            return self._colored_format(time, self._time_color)
        return ''

    @property
    def path(self) -> str:
        """Return the format fragment for the source file path, with optional color."""
        if self._show_path:
            return self._colored_format('{file.path}', self._path_color)
        return ''

    @property
    def function(self) -> str:
        """Return the format fragment for the function name, with optional color."""
        if self._show_function:
            return self._colored_format('{function}', self._function_color)
        return ''

    @property
    def line(self) -> str:
        """Return the format fragment for the line number, with optional color."""
        if self._show_line:
            return self._colored_format('{line}', self._line_color)
        return ''

    # ----------------------------------------------------------------------
    # Main method: produce the final format string
    # ----------------------------------------------------------------------

    def get_format_string(self, handler_type: str = 'console') -> str:
        """
        Generate the final log format string for loguru.

        Args:
            handler_type: Either 'console' or 'file' – selects which template to use.

        Returns:
            A string suitable for passing as `format` to loguru.add().
        """
        template = self._console_style if handler_type == 'console' else self._file_style

        # Replace replacements like '| level |' with the actual format fragments.
        # The replacements in the template are expected to be exactly these strings.
        replacements = {
            'level': self.level,
            'msg': self.msg,
            'time': self.time,
            'path': self.path,
            'function': self.function,
            'line': self.line,
        }

        result = template
        for ph, value in replacements.items():
            result = result.replace(ph, value)

        # Remove extra spaces that may appear if some replacements were empty.
        result = ' '.join(result.split())
        return result
