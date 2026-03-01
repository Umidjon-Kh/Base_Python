import argparse
import sys
from ast import literal_eval
from pathlib import Path

# project modules
from . import __version__
from .loggers import standard_logger, loguru_logger, rich_logger
from .src import Organizer, RuleManager, ConfigManager, OrganizerError


# Adding args and description for --help
def create_parser():
    parser = argparse.ArgumentParser(
        description='File organizer — sorts files into folders based on their extensions.',
        epilog='''
Examples:
  %(prog)s --version                          # show version
  %(prog)s ~/Downloads                         # sort files in‑place
  %(prog)s ~/Downloads --dest ~/Sorted         # move to ~/Sorted
  %(prog)s ~/Downloads --recursive              # process subfolders
  %(prog)s ~/Downloads --dry-run                # preview only
  %(prog)s ~/Downloads --clean-source           # remove empty dirs after

  # Custom rules
  %(prog)s ~/Downloads --rules "{'.txt': 'Texts', '.py': 'Scripts'}"
  %(prog)s ~/Downloads --rules-file my_rules.json

  # Combine default and custom rules
  %(prog)s ~/Downloads --rules "{'.md': 'Docs'}" --combine

  # Configuration file (all options can be stored in JSON)
  %(prog)s ~/Downloads --config my_config.json

  # Logging control
  %(prog)s ~/Downloads --log-file app.log --stream-level debug
  %(prog)s ~/Downloads --log-file app.log --write-level error
  %(prog)s ~/Downloads --logger loguru

Priority of settings (higher overrides lower):
  1. Command line arguments
  2. Configuration file (if given)
  3. Built‑in defaults
''',
    )

    # Positional argument
    parser.add_argument('source', help='Source folder to organize')

    # Optional arguments
    parser.add_argument('--dest', '-d', help='Destination root folder (default: source folder)')
    # Modes
    parser.add_argument('--recursive', '-R', action='store_true', help='Process subfolders recursively')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Simulate without moving files')
    parser.add_argument('--clean-source', '-C', action='store_true', help='Cleans all empty dirs in source')
    # Configs and version
    parser.add_argument('--config', help='Path to custom User configuration')
    parser.add_argument('--version', '-V', action='version', version=f'%(prog)s {__version__}')
    # Rules
    parser.add_argument('--rules', '-r', help='Custom User rules')
    parser.add_argument('--rules-file', help='JSON file with custom rules')
    parser.add_argument(
        '--combine',
        '-c',
        action='store_true',
        help='Combine deaults rules and custom User rules (needs User custom rules to combine)',
    )
    # Logging related arguments
    parser.add_argument('--log-file', help='Path to log file (if not set, logs go only to console)')
    parser.add_argument(
        '--stream-level',
        '-sl',
        default='info',
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
    parser.add_argument(
        '--logger',
        default='loguru',
        choices=['loguru', 'standard', 'rich'],
        help='Choose logger to show and write log messages ',
    )

    return parser


# Main code running in cli mode
def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    configs = ConfigManager(args, args.config).configs

    # 1.Action: Set up logging
    if configs['logger'] == 'standard':
        logger = standard_logger(configs['stream_level'], configs['log_file'], configs['write_level'])
    # elif configs['logger'] == 'rich_logger':
    elif configs['logger'] == 'rich':
        logger = rich_logger(configs['stream_level'], configs['log_file'], configs['write_level'])
    # else configs['logger'] == 'loguru': default
    else:
        logger = loguru_logger(configs['stream_level'], configs['log_file'], configs['write_level'])

    # 2.Main Action: core (file organizing)
    try:
        source_path = Path(configs['source']).resolve()
        dest_path = Path(configs['dest']).resolve() if args.dest else None
        rules_file = Path(configs['rules_file']).resolve() if args.rules_file else None

        # Initialize rule manager with rule args
        # Converting rules to dict
        rules_dict = None
        if configs['rules']:
            try:
                # Using literal_eval from ast to safety converting string to dict
                rules_dict = literal_eval(configs['rules'])
                if not isinstance(rules_dict, dict):
                    logger.error('Argument --rules must be dict object, example: "{\'.txt\': \'Docs\'}"')
                    sys.exit(1)

            except (SyntaxError, ValueError) as exc:
                logger.exception(f'Wrong format --rules:\n{exc}')
                sys.exit(1)

        rule_manager = RuleManager(rules_dict, rules_file, configs['combine'])

        # Create organizer instance
        organizer = Organizer(
            rule_manager=rule_manager,
            dest_root=dest_path,
            recursive=configs['recursive'],
            dry_run=configs['dry_run'],
            clean_source=configs['clean_source'],
        )

        # Run the organization
        organizer.organize(source_path)

    except OrganizerError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(2)


if __name__ == '__main__':
    main()
