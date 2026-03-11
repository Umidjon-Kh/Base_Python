from pathlib import Path

from ..ports import ConfigRepository, RuleRepository, FileSystem, Logger
from ..dto import OrganizeRequest, OrganizeResult
from ...exceptions import RuleNotFoundError


class OrganizeFilesUseCase:
    """
    Core business logic of the application.

    Knows only domain and application ports - no infrastructure imports.
    Receives all dependencies through __init__ (Dependency Injection).
    bootstrap() is the only place that creates this object.
    """

    def __init__(
        self,
        config_repo: ConfigRepository,
        rule_repo: RuleRepository,
        file_system: FileSystem,
        logger: Logger,
    ) -> None:
        self._config_repo = config_repo
        self._rule_repo = rule_repo
        self._file_system = file_system
        self._logger = logger

    def execute(self) -> OrganizeResult:
        """
        Run the file organization.

        Steps:
            1. Load config and rules from repositories
            2. Build OrganizeRequest from loaded data
            3. Scan source directory for files
            4. For each file: match rule -> move (or skip if dry_run)
            5. Return OrganizeResult with full summary

        Returns:
            OrganizeResult with lists of moved, skipped and errored files.
        """

        # ── 1. Load config and rules ──────────────────────────────────────────
        config = self._config_repo.load_config()
        rule_set = self._rule_repo.load_rules()

        # ── 2. Build request ──────────────────────────────────────────────────
        request = OrganizeRequest(
            source_dir=config.source_dir,
            dest_dir=config.dest_dir,
            rule_set=rule_set,
            dry_run=config.dry_run or False,
            recursive=config.recursive or False,
            ignore_patterns=config.ignore_patterns or [],
        )

        result = OrganizeResult(dry_run=request.dry_run)

        self._logger.info('Starting file organization')
        self._logger.info(f'Source    : {request.source_dir}')
        self._logger.info(f'Dest      : {request.dest_dir}')
        self._logger.info(f'Dry run   : {request.dry_run}')
        self._logger.info(f'Recursive : {request.recursive}')

        # ── 3. Scan source directory ──────────────────────────────────────────
        source_dir = self._file_system.scan(
            path=request.source_dir,
            recursive=request.recursive,
            ignore_patterns=request.ignore_patterns,
        )

        files = source_dir.children()

        self._logger.info(f'Found {len(files)} file(s) to process')

        # ── 4. Process each file ──────────────────────────────────────────────
        for file_item in files:
            try:
                # Ask RuleSet which folder this file belongs to
                # Returns: folder name str, or None if file should be skipped
                folder_name = request.rule_set.get_folder_name(file_item)

                # None means RuleSet decided to ignore this file
                if folder_name is None:
                    self._logger.debug(f'Skipped (no rule matched): {file_item.path}')
                    result.add_skipped(file_item.path)
                    continue

                # Build full destination path
                dest_path = request.dest_dir / folder_name if request.dest_dir else request.source_dir / folder_name

                if request.dry_run:
                    # Simulation - log only, do not move
                    self._logger.info(f'[DRY RUN] Would move: {file_item.path} -> {dest_path}')
                    result.add_skipped(file_item.path)
                else:
                    # Scan destination to pass as new_parent to file_system.move()
                    dest_dir = self._file_system.scan(path=dest_path, recursive=False)
                    self._file_system.move(
                        file_item=file_item,
                        destination=dest_path,
                        new_parent=dest_dir,
                        dry_run=False,
                    )
                    self._logger.info(f'Moved: {file_item.path} -> {dest_path}')
                    result.add_moved(file_item.path, dest_path)

            except RuleNotFoundError as exc:
                # other_behavior == 'raise' and no rule matched
                self._logger.warning(f'No rule for file: {file_item.path} - {exc}')
                result.add_error(file_item.path, str(exc))

            except Exception as exc:
                # Catch all other errors - one bad file should not stop the whole run
                self._logger.error(f'Failed to process: {file_item.path} - {exc}')
                result.add_error(file_item.path, str(exc))

        # ── 5. Summary ────────────────────────────────────────────────────────
        self._logger.info(
            f'Done. Moved: {len(result.moved)} | ' f'Skipped: {len(result.skipped)} | ' f'Errors: {len(result.errors)}'
        )

        return result
