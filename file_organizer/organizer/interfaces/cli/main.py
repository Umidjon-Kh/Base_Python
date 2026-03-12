import argparse
from pathlib import Path

# Project modules: main runner bootstrap, to push config ConfigOverrides
# And Organize result for showing result in user friendly output
from ...bootstrap import bootstrap, ConfigOverrides
from ...application import OrganizeResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='organizer',
        description='Organize files by rules',
    )
    # Main positional argument of directory source path
    parser.add_argument('source_dir', help='Source directory to organize')
    # Optional arguments

    # Path of destination for sorted files directory
    parser.add_argument('--dest_dir', '-d', help='Destination folder to move organized files')

    # Modes
    parser.add_argument('--recursive', '-R', action='store_true', help='Procces subfolders recursively')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Simulate actions without realization')
    parser.add_argument('--clean', '-C', action='store_true', help='Clean all empty dirs after organizing')
