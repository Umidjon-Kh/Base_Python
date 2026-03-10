from typing import Optional

# Project module: application AppConfig and port ConfigRepo
from ...application import ConfigRepository, AppConfig


class InMemoryConfigRepository(ConfigRepository):
    """
    Config repository that merges a default config with user overrides in memory.

    Follows the same pattern as InMemoryRuleRepository and InMemoryStyleRepository:
        default_repo  — always required, provides the baseline AppConfig
        config        — optional AppConfig with override values (None fields are ignored)

    No combine flag needed — merge is always automatic:
        for each field: take override value if not None, otherwise take base value.

    WHY no combine flag?
        Rules and styles need combine=False when user wants to REPLACE defaults
        entirely. Config fields are atomic values (paths, bools, dicts) — there
        is no "replace all" vs "merge" concept, only field-by-field override.
        So the merge is always the right behaviour.
    """

    __slots__ = ('_default_repo', '_config')

    def __init__(
        self,
        default_repo: ConfigRepository,
        config: Optional[AppConfig] = None,
    ) -> None:
        """
        Args:
            default_repo: Repository that provides the baseline AppConfig.
            config:       Optional AppConfig whose non-None fields override the base.
                          If None, load_config() simply returns the default config.
        """
        self._default_repo = default_repo
        self._config = config

    def load_config(self) -> AppConfig:
        base = self._default_repo.load_config()

        # No overrides — return base directly
        if self._config is None:
            return base

        return self._merge(base, self._config)

    def _merge(self, base: AppConfig, override: AppConfig) -> AppConfig:
        """
        Create a new AppConfig by taking each field from override if not None,
        otherwise from base.

        WHY is not None and not just truthiness?
            dry_run=False is a valid explicit override.
            `False or base.dry_run` would incorrectly discard it.
            `False is not None` correctly keeps it.
        """
        return AppConfig(
            source_dir=override.source_dir or base.source_dir,
            dest_dir=override.dest_dir or base.dest_dir,
            dry_run=override.dry_run if override.dry_run is not None else base.dry_run,
            recursive=override.recursive if override.recursive is not None else base.recursive,
            ignore_patterns=override.ignore_patterns if override.ignore_patterns is not None else base.ignore_patterns,
            rules_file=override.rules_file or base.rules_file,
            rules_cfg=override.rules_cfg or base.rules_cfg,
            styles_file=override.styles_file or base.styles_file,
            styles_cfg=override.styles_cfg or base.styles_cfg,
            logging=override.logging or base.logging,
        )
