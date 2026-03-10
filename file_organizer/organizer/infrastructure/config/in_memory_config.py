from ...application import ConfigRepository, AppConfig


class InMemoryConfigRepository(ConfigRepository):
    """
    In-memory config repository for testing or CLI overrides.

    Simply returns the pre-configured AppConfig instance provided at construction.
    """

    def __init__(self, config: AppConfig):
        """
        Args:
            config: The AppConfig instance to be returned by load_config().
        """
        self._config = config

    def load_config(self) -> AppConfig:
        return self._config
