import logging
from pathlib import Path
from shutil import move
from typing import Optional
from .rules import RuleManager
from .exceptions import PathError

logger = logging.getLogger(__name__)


# core
class Organizer:
    """
    Organizes files to folders with their extention
    according to rules from RuleManager
    """

    __slots__ = ('rule_manager', 'dest_root', 'recursive', 'dry_run', 'stats')

    # Initializing attrs
    def __init__(
        self,
        rule_manager: RuleManager,
        dest_root: Optional[Path] = None,
        recursive: bool = False,
        dry_run: bool = False,
    ) -> None:
        """
        :param  rule_manager: Manager of rules
        :param dest_root: root folder to move organize (if None, uses current path)
        :param recursive: process sub folders recursively
        :param dry_run: if True, only lofs and shows all action without realization
        :param stats: To show actions stats
        """

        self.rule_manager = rule_manager
        self.dest_root = dest_root
        self.recursive = recursive
        self.dry_run = dry_run
        self.stats = {'moved': 0, 'skipped': 0, 'errors': 0, 'planned': 0}

    # Organizer core method
    def organize(self, source: Path) -> None:
        """Runnning process of file organizing"""
        # 1.Action: Checking for source path
        if not source.exists():
            raise PathError(f'Source folder is not exists: {source}')
        if not source.is_dir():
            raise PathError(f'The source path is not a folder: {source}')

        # 2.Action: If the destination root isn't set, use the source
        dest_root = self.dest_root if self.dest_root else source
        logger.info(f'Starting organization. Source: {source}, destination: {dest_root}')
        logger.info(f'Modes: recursive: {self.recursive}, dry run: {self.dry_run}')

        # 3.Action: organizing
        # 1.Scenario: if recursive True
        if self.recursive:
            # Recursively processing sub folders
            for item in source.rglob('*'):
                if item.is_file():
                    self._process_file(item, dest_root)
        # 2.Scenario: If not recursive only in folder
        else:
            for item in source.iterdir():
                if item.is_file():
                    self._process_file(item, dest_root)

        # Logging stats
        logger.info(
            f'Final stats — Moved: {self.stats['moved' if not self.dry_run else 'planned']},'
            f' Skipped: {self.stats['skipped']},'
            f' Errors: {self.stats['errors']}'
        )

    # processing files
    def _process_file(self, file_path: Path, dest_root: Path) -> None:
        """Process a single file: determine destination folder and move it."""
        try:
            # 1.Action: getting all path to move
            ext = file_path.suffix
            target_folder_name = self.rule_manager.get_folder(ext)
            target_dir = dest_root / target_folder_name
            target_path = target_dir / file_path.name

            # 2.Action moving file to dest
            # 1.Scenario: If file is already in destination path
            if file_path.parent == target_dir:
                logger.debug(f'Skipping (already in destionation folder): {file_path}')
                self.stats['skipped'] += 1
                return

            # handling name collisions
            if target_path.exists():
                base = target_path.stem
                suffix = target_path.suffix
                counter = 1
                while target_path.exists():
                    new_name = f'{base}({counter}){suffix}'
                    target_path = target_dir / new_name
                    counter += 1

            # 2.Scenario: If dry_run is True
            if self.dry_run:
                logger.info(f'[DRY RUN] Moves:\nFile: {file_path}\n\t\t\t└──> {target_path}')
                self.stats['planned'] += 1
                return

            # Creating destination path
            target_dir.mkdir(parents=True, exist_ok=True)

            # Moving file to dest
            move(file_path, target_path)
            logger.info(f'Moved:\n{file_path}\n\t\t└──>{target_path}')
            self.stats['moved'] += 1

        except Exception as exc:
            logger.error(f'Error while processing:\nFile:{file_path}\nError:{exc}')
            self.stats['errors'] += 1
