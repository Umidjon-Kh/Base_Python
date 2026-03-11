from ..ports import ConfigRepository, RuleRepository, FileSystem, Logger
from ..dto import OrganizeRequest, OrganizeResult
from ...domain import Directory
from ...exceptions import RuleNotFoundError


class OrganizeFilesUseCase:
    """
    Core business logic of the application.

    Knows only domain and application ports - no infrastructure imports.
    Receives all dependencies through __init__ (Dependency Injection).
    bootstrap() is the only place that creates and calls this object.
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
            3. Scan source directory -> Directory tree
            4. Walk files via walk_files() generator (memory efficient)
            5. For each file: get folder from RuleSet -> mkdir -> move
            6. Return OrganizeResult with full summary
        """

        # Loading configs from ConfigRepository
        config = self._config_repo.load_config()
        rule_set = self._rule_repo.load_rules()

        # Building user request data cls
        request = OrganizeRequest(
            source_dir=config.source_dir,  # type: ignore
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

        # Scan source root directory with file_system
        source_dir = self._file_system.scan(
            path=request.source_dir,
            recursive=request.recursive,
            ignore_patterns=request.ignore_patterns,
        )

        # Running directory root walk files method to yield all files one by one
        # For optimizing and economy memory resources
        for file_item in source_dir.walk_files():
            try:
                # Asking RuleSetter for folder name
                folder_name = request.rule_set.get_folder_name(file_item)

                # If folder name in ignore list or rule is to ignore those like folders
                if folder_name is None:
                    self._logger.debug(f'Skipped: {file_item.name}')
                    result.add_skipped(file_item.path)
                    continue

                # Build destination path: dest_dir/folder_name
                base = request.dest_dir if request.dest_dir is not None else request.source_dir
                dest_path = base / folder_name

                # Create Directory object so file_system.move() can update the tree
                new_parent = Directory(dest_path)

                # move() handles dry_run internally - no physical move if dry_run=True
                # move() also handles mkdir and name collision resolution
                self._file_system.move(
                    file_item=file_item,
                    destination=dest_path,
                    new_parent=new_parent,
                    dry_run=request.dry_run,
                )

                # In dry_run we still record as moved - user wants to see what WOULD happen.
                # OrganizeResult.dry_run=True already signals this was a simulation.
                prefix = '[DRY RUN] ' if request.dry_run else ''
                self._logger.info(f'{prefix}Moved: {file_item.name} -> {dest_path}')
                result.add_moved(file_item.path, dest_path)

            except RuleNotFoundError as exc:
                # other_behavior == 'raise' and no rule matched
                self._logger.warning(f'No rule matched: {file_item.name} - {exc}')
                result.add_error(file_item.path, str(exc))

            except Exception as exc:
                # One bad file must not stop the whole run
                self._logger.error(f'Failed: {file_item.path} - {exc}')
                result.add_error(file_item.path, str(exc))

        # Showing Summary of actions
        self._logger.info(
            f'Done.  Moved: {len(result.moved)} |',
            f'Skipped: {len(result.skipped)} | ',
            f'Errors: {len(result.errors)}',
        )

        return result
