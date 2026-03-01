from loguru import logger
from pathlib import Path
from shutil import move
from typing import Optional

# Project modules
from .rule_manager import RuleManager
from .exceptions import PathError


class Organizer:
    """
    Main core cls that works with files
    And Organizes tham by extension type
    Uses RuleManager to set extension for folder
    """

    __slots__ = ('rule_manager', 'dest', 'recursive', 'dry_run', 'clean', 'stats')

    def __init__(
        self,
        rule_manager: RuleManager,
        dest: Optional[str] = None,
        recursive: bool = False,
        dry_run: bool = False,
        clean: bool = False,
    ) -> None:
        """
        :param rule_manager: Manager of rules
        :param dest: root folder to organize (if None, uses source folder)
        :param recursive: Process all sub folders from source recursively
        :param dry_run: If True, only shows all action without realizing
        :param clean: If True cleans all source path empty folders after organizing
        :param stats: To shows action stats
        """

        self.rule_manager = rule_manager
        self.dest = dest
        self.recursive = recursive
        self.dry_run = dry_run
        self.clean = clean
        self.stats = {
            'moved': 0,
            'removed': 0,
            'skipped': 0,
            'errors': 0,
        }

    # Organizer core method
    def organize(self, source: str) -> None:
        """Running procces of file organizing"""
        # 1.Action checking source path for existing and is dir
        path = Path(source).resolve()
        if not path.exists():
            raise PathError(f'Source "{path.name}" is not exists')
        if not path.is_dir():
            raise PathError(f'The source "{path.name}" is not a folder')

        # 2.Action: Creating destination for organized folders
        dest = Path(self.dest).resolve() if self.dest else path
        logger.info(f'Starting organizer: Source: {path}. Destination: {dest}')
        logger.info('Modes:')
        logger.info(f'[Recursive]: {self.recursive}')
        logger.info(f'[Dry Run]: {self.dry_run}')
        logger.info(f'[Clean]: {self.clean}')

        # 3.Action: Organizing
        # 1.Scenario: If Recursive mode is on
        if self.recursive:
            # Recursively processing sub folders
            for item in path.rglob('*'):
                if item.is_file():
                    self._process_file(item, dest)
        # 2.Scenario: If Recursive mode is off
        else:
            for item in path.iterdir():
                if item.is_file():
                    self._process_file(item, dest)

        # 4.Action: If Clean mode is on
        if self.clean:
            # Removing all empty dirs if not in mode dry_run
            self._rm_empty_dirs(path)

        # 5.Action: Showing all actions in logging mode
        mv = 'Moved' if not self.dry_run else 'Moves'
        rm = 'Removed' if not self.dry_run else 'Removes'
        sk = 'Skipped' if not self.dry_run else 'Skips'

        logger.success('Succes all actions is completed')
        logger.info('Actions in session:')
        logger.info(f'\t{mv} - {self.stats['moved']}')
        logger.info(f'\t{rm} - {self.stats['removed']}')
        logger.info(f'\t{sk} - {self.stats['skipped']}')
        logger.info(f'\tErrors - {self.stats['errors']}')

    # processing files
    def _process_file(self, file_path: Path, dest: Path) -> None:
        """Process a single file: determine destination folder and move it"""
        try:
            # 1.Action: Getting destination folder path to move
            ext = file_path.suffix
            folder = self.rule_manager.get_folder(ext)
            directory = dest / folder
            path = directory / file_path.name

            # 2.Action: Moving file to destination
            # 1.Scenario: If file is already in destionation
            if file_path.parent == directory:
                logger.debug(f'Skipping already in destionation folder: {file_path.stem}')
                self.stats['skipped'] += 1
                return

            # 2.Scenario: If not in destination
            # Handling Collisons firstly
            # And looping while we rich not exited name of file
            if path.exists():
                base = path.stem
                suffix = path.suffix
                counter = 1
                while path.exists():
                    new_name = f'{base}_({counter}){suffix}'
                    path = directory / new_name
                    counter += 1

            # If Dry Run mode is on
            # We dont move only show info and add action type
            if self.dry_run:
                logger.info(f'[Dry Run] Moves: {file_path} --> {path}')
                self.stats['moved'] += 1
                return

            # Creating destination path if not dry run
            directory.mkdir(parents=True, exist_ok=True)

            # MOving file to destination
            move(file_path, path)
            logger.info(f'Moved: {file_path} --> {path}')
            self.stats['moved'] += 1

        except Exception as exc:
            logger.error(f'Error while processing | File: {file_path} | Error: {exc}')
            self.stats['errors'] += 1

    # Removing empty folders method
    def _rm_empty_dirs(self, source: Path) -> None:
        """
        Recursively removes empty directories
        After Organizing
        Not works in Dry Run mode only shows which one would be removed
        """

        # Getting all path of dirs from source: from down to up
        for path in sorted(source.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir():
                # Only removes dir if its empty
                try:
                    if not any(path.iterdir()):
                        if self.dry_run:
                            logger.debug(f'[Dry Run] Removes empty dir: {path}')
                            self.stats['removed'] += 1
                            continue
                        path.rmdir()
                        logger.warning(f'Removed empty dir: {path}')
                        self.stats['removed'] += 1
                except PermissionError:
                    pass
