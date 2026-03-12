import argparse
import json
import re

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
        config_files=args.config or None,
        recursive=args.recursive or None,
        dry_run=args.dry_run or None,
        clean_mode=args.clean or None,
        ignore_patterns=ignore_patterns,
        rules_cfg=rules_cfg,
        rules_file=args.rules_file or None,
        rules_combine=args.combine_rules or None,
        styles_cfg=styles_cfg,
        styles_file=args.styles_file or None,
        styles_combine=args.combine_styles or None,
        console_level=args.console_level,
        log_file=args.log_file,
        file_level=args.file_level,
    )


def _visible_len(string: str) -> int:
    """Returns string length without ANSI codes"""
    return len(re.sub(r'\033\[[0-9;]*m', '', string))


def _pad(string: str, width: int) -> str:
    """Auto puts needed spaces even with ANSI color codes"""
    return string + ' ' * (width - _visible_len(string))


def show_result(result: OrganizeResult) -> None:
    WIDTH = 40  # width of result bar without(|)

    # Modes
    mode_parts = []
    if result.dry_run:
        mode_parts.append(f'{YELLOW}DRY RUN{RESET}')
    if result.clean_mode:
        mode_parts.append(f'{CYAN}CLEAN{RESET}')
    if result.recursive:
        mode_parts.append(f'{CYAN}RECURSIVE{RESET}')
    mode_str = ' · '.join(mode_parts)

    def row(content: str) -> str:
        return f'  {BOLD}│{RESET} {_pad(content, WIDTH)} {BOLD}│{RESET}'

    def divider(left='├', mid='─', right='┤') -> str:
        return f'  {BOLD}{left}{mid * (WIDTH + 2)}{right}{RESET}'

    # Header
    title = f'{PURPLE}{BOLD}✦ klart{RESET}'
    modes = f'  {mode_str}' if mode_str else ''

    print()
    print(divider('╭', '─', '╮'))
    print(row(title + modes))
    print(divider())

    # Error
    if result.errors:
        print(row(f'{RED}{BOLD}Errors{RESET}'))
        print(divider())
        for path, message in result.errors:
            name = str(path)
            if len(name) > WIDTH - 2:
                name = '…' + name[-(WIDTH - 3):]
            print(row(f'{RED}✗{RESET} {DIM}{name}{RESET}'))
            msg = message[: WIDTH - 4]
            print(row(f'  {DIM}↳ {msg}{RESET}'))
        print(divider())

    # Actions Summary
    def summary_row(icon: str, color: str, label: str, count: int) -> str:
        left = f'{color}{icon}{RESET}  {label}'
        right = f'{color}{BOLD}{count}{RESET}'
        spaces = WIDTH - _visible_len(left) - _visible_len(right)
        return f'  {BOLD}│{RESET} {left}{" " * spaces}{right} {BOLD}│{RESET}'

    print(summary_row('✔', GREEN, 'Moved  ', len(result.moved)))
    print(summary_row('●', YELLOW, 'Skipped', len(result.skipped)))
    print(summary_row('◆', DARKCYAN, 'Removed', len(result.removed)))
    print(summary_row('✗', RED, 'Errors ', len(result.errors)))
    print(divider())

    # Status of finished procces
    if result.success:
        print(row(f'{GREEN}{BOLD}✦  All done.{RESET}'))
    else:
        print(row(f'{RED}{BOLD}✦  Finished with errors.{RESET}'))
    print(divider('╰', '─', '╯'))
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
