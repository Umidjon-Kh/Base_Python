# Project modules: AppConfig to save data and port of ConfigRepo
from ...application import ConfigRepository, AppConfig


class InMemoryConfigRepository(ConfigRepository):
    """
    In-memory config repository that holds a pre-built AppConfig.

    WHY SO SIMPLE?
        All config merging (3 layers) happens in _build_config() inside bootstrap.py.
        By the time this object is created, the AppConfig is already fully merged.
        This class just wraps it so use cases receive it through the ConfigRepository
        port interface instead of depending on AppConfig directly.

        InMemoryConfigRepository(config)  ← bootstrap passes the final merged config
        use_case.execute(config_repo)     ← use case calls load_config(), gets AppConfig
    """

    __slots__ = ('_config',)

    def __init__(self, config: AppConfig) -> None:
        """
        Args:
            config: The final fully merged AppConfig produced by bootstrap._build_config().
        """
        self._config = config

    def load_config(self) -> AppConfig:
        return self._config
