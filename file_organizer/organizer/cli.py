import argparse

# Project modules
from . import __version__
from .logger import LogManager
from .src import Organizer, RuleManager, ConfigManager, OrganizerError


# Adding args and description
def create_parser():
    parser = argparse.ArgumentParser(
        description='File organizer - sorts files into folders based on their extensions',
        epilog='''
Examples:
  %(prog)s --version        # shows version of organizer
  %(prog)s --help           #shows this help menu
  %(prog)s ~/Downloads      # sort files in-place
  %(prog)s ~/Downloads --dest ~/Sorted     # move to ~/Sorted
  %(prog)s ~/Downloads --recursive         # process subfolders recursively
  %(prog)s ~/Downloads --dry-run           # previev action without realization
  %(prog)s ~/Downloads --clean     # remove empty dirs after organizing
  # Custom rules
  %(prog)s ~/Downloads --rules "{'.txt': 'Texts', '.py': 'Scripts'}"
  %(prog)s ~/Downloads --rules-file my_rules.json

  # Combine default and custom user rules
  %(prog)s ~/Downloads --rules "{'.txt': 'Texts', '.py': 'Scripts'}" --combine
  
  # Configuration file (all options can be stored in JSON)
  %(prog)s ~/Downloads --config  my_config.json

  # Logging control
  %(prog)s ~/Downloads --log-file app.log --stream-level debug
  %(prog)s ~/Downloads --log-file app.log --write-level error
  %(prog)s ~/Downloads --log-file app.log --style minimalistic
      #  If you want to set style for file_logger or set your
      #  own style plase use json file for your configs

Priority of settings (higher overrides lower):
  1. Command line arguments
  2. Configuration file (if given)
  3. Built‑in defaults
''',
    )

    # Positional required argumnet
    parser.add_argument('source', help='Source folder to organize')

    # Optional argumnets
    parser.add_argument('--dest', '-d', help='Destination folder to move organized files')
    # Modes
    parser.add_argument('--recursive', '-R', action='store_true', help='Process subfolders recursively')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Simulate actions without realization')
    parser.add_argument('--clean', '-C', action='store_true', help='Cleans empty dirs from source after organization')
    # Configs
    parser.add_argument('--config', help='Path to custom User configuration')
    # Version
    parser.add_argument('--version', '-V', action='version', version=f'%(prog)s {__version__}')
    # Rules
    parser.add_argument('--rules', '-r', help='Custom User rules')
    parser.add_argument('--rules-file', help='JSON FILE with custom User rules')
    parser.add_argument(
        '--combine',
        '-c',
        action='store_true',
        help='Combine default rules with custom User rules'
    )
    # Logging related arguments
    parser.add_argument(
        '--stream-level',
        '-sl',
        default='info',
        choices=['debug', 'info', 'succes', 'warning', 'error', 'critical'],
        help='Log level for console output (default: debug)')
    parser.add_argument(
        '--write-level',
        '-wl',
        default='debug',
        choices=['debug', 'info', 'succes', 'warning', 'error', 'critical'],
        help='Log level for saving to file (default: debug)')
    parser.add_argument('--log-file', help='Path to save log file')
    parser.add_argument(
        '--style',
        default='simple',
        choices=['simple', 'modern', 'split', 'minimalistic']
        help='Choose log style format'
    )

    return parser