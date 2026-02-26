import argparse
import sys
from ast import literal_eval
from pathlib import Path

# project modules
from .logger import setup_logger
from .rules import RuleManager
from .core import Organizer
from .exceptions import OrganizerError


def create_parser():
    parser = argparse.ArgumentParser(
        description='File organizer — sorts files into folders based on their extensions.',
        epilog='''
Examples:
  %(prog)s ~/Downloads                     # sort files in-place, console level: INFO (default)
  %(prog)s ~/Downloads --dest ~/Sorted     # move files to ~/Sorted
  %(prog)s ~/Downloads --recursive         # process subfolders recursively
  %(prog)s ~/Downloads --dry-run           # dry run (no actual moves)
  %(prog)s ~/Downloads --rules my_rules.json  # use custom rules from JSON file
  %(prog)s ~/Downloads --stream-level debug   # detailed console output (DEBUG level)
  %(prog)s ~/Downloads --log-file app.log      # write logs to file (default level DEBUG)
  %(prog)s ~/Downloads --log-file app.log --write-level error  # file logs only errors
  %(prog)s ~/Downloads --stream-level warning --log-file app.log --write-level debug
                    # console: warnings+, file: all messages
        ''',
    )

    # Positional argument
    parser.add_argument('source', help='Source folder to organize')

    # Optional arguments
    parser.add_argument('--dest', '-d', help='Destination root folder (default: source folder)')
    parser.add_argument('--rules', '-r', help='Custom User rules')
    parser.add_argument('--rule-file', help='JSON file with custom rules')
    parser.add_argument(
        '--combine',
        '-c',
        action='store_true',
        help='Combine deaults rules and custom User rules (needs User custom rules to combine)',
    )
    parser.add_argument('--recursive', '-R', action='store_true', help='Process subfolders recursively')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Simulate without moving files')

    # Logging related arguments
    parser.add_argument('--log-file', help='Path to log file (if not set, logs go only to console)')
    parser.add_argument(
        '--stream-level',
        '-sl',
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

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    # 1.Action: Set up logging
    # If dry run mode is on we need to set
    # stream level to debug to show all changes
    if args.dry_run:
        stream_level = 'debug'
    else:
        stream_level = args.stream_level

    logger = setup_logger(stream_level=stream_level, log_file=args.log_file, write_level=args.write_level)

    # 2.Main Action: core (file organizing)
    try:
        source_path = Path(args.source).resolve()
        dest_path = Path(args.dest).resolve() if args.dest else None

        # Initialize rule manager with rule args
        # Converting rules to dict
        rules_dict = None
        if args.rules:
            try:
                # Using literal_eval from ast to safety converting string to dict
                rules_dict = literal_eval(args.rules)
                if not isinstance(rules_dict, dict):
                    logger.error('Argument --rules must be dict object, example "{\'.txt\': \'Docs\'}"')
                    sys.exit(1)

            except (SyntaxError, ValueError) as exc:
                logger.exception(f'Wrong format --rules:\n{exc}')
                sys.exit(1)

        rule_manager = RuleManager(rules=rules_dict, rules_file=args.rule_file, combine=args.combine)

        # Create organizer instance
        organizer = Organizer(
            rule_manager=rule_manager, dest_root=dest_path, recursive=args.recursive, dry_run=args.dry_run
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
