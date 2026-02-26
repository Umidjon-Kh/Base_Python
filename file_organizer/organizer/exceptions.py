class OrganizerError(BaseException):
    """Base exception for organizer"""

    pass


class RuleError(OrganizerError):
    """Error in sorting rules"""

    pass


class PathError(OrganizerError):
    """Error related to paths"""

    pass
