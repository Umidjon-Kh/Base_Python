"""All Exceptions for Organizer package"""


class OrganizerError(Exception):
    """
    Main core excpetions triggers all sub errors:
    1) RuleError: wrong format of rules error
    2) PathError: wrong path or smething went wrong while loading from file error
    3) StyleError: wrong format of styles error
    4) ConfigError: wrong format of config params error
    """

    pass


class ConfigError(OrganizerError):
    """Triggers if format of config params is wrong"""

    pass


class RuleError(ConfigError):
    """Triggers if format of rules is wrong"""

    pass


class StyleError(ConfigError):
    """Triggers if format of styles for log is wrong"""

    pass


class PathError(ConfigError):
    """Triggers if something goes wrong while loading"""

    pass
