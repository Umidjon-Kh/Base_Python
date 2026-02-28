class OrganizerError(BaseException):
    """Main Organizer core error"""

    pass


class ConfigError(OrganizerError):
    """Configurer Error"""

    pass


class RuleError(OrganizerError):
    """RuleManager Error"""

    pass


class PathError(OrganizerError):
    """Path Error"""

    pass
