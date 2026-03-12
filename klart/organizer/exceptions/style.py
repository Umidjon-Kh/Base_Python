from .base import InfrastructureError


# ----- Style errors -----
class StyleError(InfrastructureError):
    """Base class for style loading/parsing errors"""

    pass


class StyleFileNotFoundError(StyleError):
    """Raises when styles file is not found"""

    pass


class StyleFormatError(StyleError):
    """Raises when got wrong format of style"""

    pass


class StyleNotFoundError(StyleError):
    """Raises when style is not found"""

    pass


class UnknownStyleType(StyleError):
    """Raises when Style is unnaceptable (e.g., 'web' not implemented)"""

    pass
