import argparse
import json

# Project modules: main runner bootstrap, to push config ConfigOverrides
# And Organize result for showing result in user friendly output
from ...bootstrap import bootstrap, ConfigOverrides
from ...application import OrganizeResult

# Other need exteptions
from organizer.exceptions import ConfigValidationError

# Version
from ... import __version__


# ANSI colors for showing result
RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
UNDERLINE = '\033[4m'
RED = '\033[31m'
WHITE = '\033[37m'
DIM = '\033[2m'


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='organizer',
        description='Organize files into folders based on configurable rules.',
        epilog=(
            'Examples:\n'
            '  organizer ~/Downloads\n'
            '  organizer ~/Downloads --dest ~/Sorted --recursive\n'
            '  organizer ~/Downloads --dry-run\n'
            '  organizer ~/Downloads --rules-file my_rules.json --combine-rules\n'
            '\n'
            'Config priority (highest wins):\n'
            '  CLI args > --config file > built-in defaults'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f'%(prog)s {__version__}',
    )

    # Positional
    parser.add_argument(
        'source_dir',
        nargs='?',
        help='Source directory to organize (can also be set in config file)',
    )

    # Paths
    parser.add_argument(
        '--dest',
        '-d',
        dest='dest_dir',
        metavar='DIR',
        help='Destination folder for organized files (default: inside source)',
    )
    parser.add_argument(
        '--config',
        metavar='FILE',
        help='Path to custom JSON config file',
    )

    # Ignore patterns
    parser.add_argument('--ignore', nargs='+', metavar='PATTERN', help='Ignore folders or files with this extension')

    # Modes
    parser.add_argument(
        '--recursive',
        '-R',
        action='store_true',
        help='Process subdirectories recursively',
    )
    parser.add_argument(
        '--dry-run',
        '-n',
        action='store_true',
        help='Simulate actions without moving any files',
    )
    parser.add_argument(
        '--clean',
        '-C',
        action='store_true',
        help='Remove empty directories after organizing',
    )

    # Rules
    parser.add_argument(
        '--rules',
        '-r',
        metavar='JSON',
        help='Inline rules config as JSON string',
    )
    parser.add_argument(
        '--rules-file',
        metavar='FILE',
        help='Path to custom rules JSON file',
    )
    parser.add_argument(
        '--combine-rules',
        '-cr',
        action='store_true',
        help='Combine custom rules with built-in defaults (instead of replacing)',
    )

    # Styles
    parser.add_argument(
        '--styles',
        '-s',
        metavar='JSON',
        help='Inline styles config as JSON string',
    )
    parser.add_argument(
        '--styles-file',
        metavar='FILE',
        help='Path to custom styles JSON file',
    )
    parser.add_argument(
        '--combine-styles',
        '-cs',
        action='store_true',
        help='Combine custom styles with built-in defaults (instead of replacing)',
    )

    # Logging
    parser.add_argument(
        '--console-level',
        '-cl',
        metavar='LEVEL',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Console log level (default: info)',
    )
    parser.add_argument(
        '--log-file',
        metavar='FILE',
        help='Path to save log file',
    )
    parser.add_argument(
        '--file-level',
        '-fl',
        metavar='LEVEL',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='File log level (default: debug)',
    )

    return parser


def args_to_overrides(args: argparse.Namespace) -> ConfigOverrides:

    # --rules и --styles пparse from json
    rules_cfg = None
    if args.rules is not None:
        try:
            rules_cfg = json.loads(args.rules)
        except json.JSONDecodeError as exc:
            raise ConfigValidationError(f'Invalid JSON in --rules: {exc}') from exc

    styles_cfg = None
    if args.styles is not None:
        try:
            styles_cfg = json.loads(args.styles)
        except json.JSONDecodeError as exc:
            raise ConfigValidationError(f'Invalid JSON in --styles: {exc}') from exc

    # --ignore can be more than one
    ignore_patterns = args.ignore if args.ignore else None

    return ConfigOverrides(
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        config_files=args.config,
        recursive=args.recursive or None,
        dry_run=args.dry_run or None,
        clean_mode=args.clean or None,
        ignore_patterns=ignore_patterns,
        rules_cfg=rules_cfg,
        rules_file=args.rules_file,
        rules_combine=args.combine_rules or None,
        styles_cfg=styles_cfg,
        styles_file=args.styles_file,
        styles_combine=args.combine_styles or None,
        console_level=args.console_level,
        log_file=args.log_file,
        file_level=args.file_level,
    )


def show_result(result: OrganizeResult) -> None:

    # Collecting on modes to shows
    mode_parts = []
    if result.dry_run:
        mode_parts.append(f'{YELLOW}DRY RUN{RESET}')
    if result.clean_mode:
        mode_parts.append(f'{CYAN}CLEAN{RESET}')
    if result.recursive:
        mode_parts.append(f'{CYAN}RECURSIVE{RESET}')

    mode_str = f'  [{" | ".join(mode_parts)}]' if mode_parts else ''

    print()
    print(f'{BOLD}{"-" * 40}{RESET}')
    print(f'{BOLD} Organizer{RESET}{mode_str}')
    print(f'{BOLD}{"-" * 40}{RESET}')

    # Errors if erros occured while organizing
    if result.errors:
        print(f'\n{BOLD}{RED} Errors:{RESET}')
        for path, message in result.errors:
            print(f'  {RED}error:{RESET} {DIM}{path}{RESET}')
            print(f'    {DIM}msg: {message}{RESET}')

    # Action summary
    print()
    print(f'  {GREEN}-- Moved   {RESET}  {BOLD}{len(result.moved)}{RESET}')
    print(f'  {YELLOW}-- Skipped {RESET}  {BOLD}{len(result.skipped)}{RESET}')
    print(f'  {DARKCYAN}--Removed {RESET} {BOLD}{len(result.removed)}{RESET}')
    print(f'  {RED}-- Errors  {RESET}  {BOLD}{len(result.errors)}{RESET}')
    print(f'{BOLD}{"-" * 40}{RESET}')

    # ── Итоговый статус ───────────────────────────────────────────────────────
    if result.success:
        print(f'  {GREEN}{BOLD}Done.{RESET}')
    else:
        print(f'  {RED}{BOLD}Finished with errors.{RESET}')
    print()


def main() -> None:
    # getting args
    parser = build_parser()
    args = parser.parse_args()

    # Arguments for bootsrap
    overrides = args_to_overrides(args)
    result = bootstrap(overrides)
    show_result(result)


if __name__ == '__main__':
    main()
