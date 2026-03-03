import argparse

# project modules
from .runner import runner
from .. import __version__


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and returns the argument parser for the organizer CLI.
    """
    parser = argparse.ArgumentParser(
        description='File organizer — sorts files into folders based on their extensions.',
        epilog=f'''
Examples:
  %(prog)s ~/Downloads                    # sort files in‑place (defaults)
  %(prog)s ~/Downloads --dest ~/Sorted    # move files to ~/Sorted
  %(prog)s ~/Downloads --recursive        # process subfolders
  %(prog)s ~/Downloads --dry-run          # preview only
  %(prog)s ~/Downloads --clean            # remove empty dirs after organization

  # Custom rules
  %(prog)s ~/Downloads --rules "{{'.txt': 'Texts', '.py': 'Scripts'}}"
  %(prog)s ~/Downloads --rules-file my_rules.json

  # Combine default and custom rules
  %(prog)s ~/Downloads --rules "{{'.md': 'Docs'}}" --combine

  # Configuration file (all options can be stored in JSON)
  %(prog)s ~/Downloads --config my_config.json

  # Logging control (requires loguru installed)
  %(prog)s ~/Downloads --stream-level debug --log-file app.log --write-level error

  # Show version
  %(prog)s --version

Priority of settings (higher overrides lower):
  1. Command line arguments
  2. Configuration file (if given)
  3. Built‑in defaults

Project: https://github.com/Umidjon-kh/Base_Python/tree/main/file_organizer
Version: {__version__}
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Positional argument
    parser.add_argument('source', help='Source folder to organize (required)')

    # Core options
    parser.add_argument('--dest', '-d', help='Destination root folder (default: source folder)')
    parser.add_argument('--recursive', '-R', action='store_true', help='Process subfolders recursively')
    parser.add_argument(
        '--dry-run',
        '-n',
        action='store_true',
        help='Simulate without moving files (automatically sets console log level to debug)',
    )
    parser.add_argument(
        '--clean', '-C', action='store_true', help='Remove empty directories in source after organization'
    )

    # Rule options
    parser.add_argument('--rules', '-r', help='Custom rules as a Python dictionary string, e.g. "{\'.txt\': \'Docs\'}"')
    parser.add_argument('--rules-file', help='JSON file containing custom rules')
    parser.add_argument(
        '--combine',
        '-c',
        action='store_true',
        help='Combine user rules with built‑in defaults (user rules take precedence)',
    )

    # Config file
    parser.add_argument(
        '--config', help='Path to a JSON configuration file (overrides defaults, but CLI arguments take precedence)'
    )

    # Logging options
    parser.add_argument('--log-file', help='Path to log file (if not set, logs go only to console)')
    parser.add_argument(
        '--stream-level',
        '-sl',
        default='debug',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Log level for console output (default: debug)',
    )
    parser.add_argument(
        '--write-level',
        '-wl',
        default='debug',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Log level for file output (default: debug; only used if --log-file is given)',
    )
    parser.add_argument('--style', default='simple', help='Log style name (defined in styles file, default: simple)')

    # Version
    parser.add_argument('--version', '-V', action='version', version=f'%(prog)s {__version__}')

    return parser


def main() -> None:
    """
    Entry point for the CLI. Parses arguments and calls the runner.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Everything is delegated to the runner
    runner(args, config_path=args.config)
