from loguru import logger

# Project modules
from domain.rules import RuleSet
from domain.entities import Directory, FileItem
from application.ports import FileSystem
from application.dto import OrganizeRequest
from domain.exceptions import RuleNotFoundError, FileSystemError


class OrganizeFiles:
    """
    Main use case: organize files according to rules.
    """

    def __init__(self, file_system: FileSystem, rule_set: RuleSet):
        self.file_system = file_system
        self.rule_set = rule_set
        self.stats = {
            'moved': 0,
            'skipped': 0,
            'errors': 0,
            'removed': 0,
        }

    def execute(self, request: OrganizeRequest) -> None:
        """Run the organization process."""
        # 1. Scan source directory with ignore patterns
        root = self.file_system.scan(
            request.source, recursive=request.recursive, ignore_patterns=request.ignore_patterns
        )

        # 2. Process all files (walk_files is recursive, but if scan was non‑recursive,
        #    subdirectories are empty, so only top‑level files are processed)
        for file_item in root.walk_files():
            self._process_file(file_item, request)

        # 3. Clean empty directories if requested
        if request.clean:
            self._clean_empty_dirs(root, request.dry_run)

        # 4. Log final stats
        self._log_stats(request.dry_run)

    def _process_file(self, file_item: FileItem, request: OrganizeRequest) -> None:
        """Handle a single file: decide destination and move."""
        try:
            # Getting destination folder to move organized file_items
            target_folder = self.rule_set.get_target_folder(file_item)
            if target_folder is None:
                logger.debug(f'Ignoring {file_item.name}')
                self.stats['skipped'] += 1
                return

            # Creating new Directory intances of new organized Directory
            dest_to_organize = Directory(request.dest or request.source)
            dest_target_folder = dest_to_organize.path / target_folder
            dest_target_folder = Directory(dest_target_folder, dest_to_organize)
            dest_target_file = dest_target_folder.path / file_item.name

            # Moving only if not dry run if dry run only changes attrs of file_item no moves
            self.file_system.move(file_item, dest_target_file, dest_target_folder, request.dry_run)
            mv_word = 'Moved' if not request.dry_run else '[DRY RUN] Would move'
            logger.info(f'{mv_word}: {file_item.path} -> {dest_target_file}')
            self.stats['moved'] += 1

        except RuleNotFoundError as exc:
            logger.error(str(exc))
            self.stats['errors'] += 1
        except FileSystemError as exc:
            logger.error(f'File system error: {exc}')
            self.stats['errors'] += 1
        except Exception as exc:
            logger.exception(f'Unexpected error processing {file_item.name}: {exc}')
            self.stats['errors'] += 1

    def _clean_empty_dirs(self, root: Directory, dry_run: bool):
        """
        Remove empty directories recursively.
        Traverse the tree bottom-up and delete empty directories.
        """
        # Collect all directories in post-order (children first)
        dirs_to_check = []

        def collect_dirs(dir: Directory):
            for child in dir.children:
                if isinstance(child, Directory):
                    collect_dirs(child)
            dirs_to_check.append(dir)

        collect_dirs(root)

        for dir in dirs_to_check:
            if dir.is_empty():
                try:
                    self.file_system.rmdir(dir, dry_run)
                    rm_word = 'Removed' if not dry_run else '[DRY RUN] Would remove'
                    logger.info(f'{rm_word} empty dir: {dir}')
                except FileSystemError as exc:
                    logger.error(f'Failed to remove {dir.path}: {exc}')
                    self.stats['errors'] += 1

    def _log_stats(self, dry_run: bool):
        moved_word = 'Moved' if not dry_run else 'Would move'
        remove_word = 'Removed' if not dry_run else 'Would remove'
        skip_word = 'Skipped' if not dry_run else 'Would skip'
        logger.info(f'{moved_word}: {self.stats['moved']}')
        logger.info(f'{skip_word}: {self.stats['skipped']}')
        logger.info(f'{remove_word} empty dirs: {self.stats['removed']}')
        logger.info(f'Errors: {self.stats['errors']}')
