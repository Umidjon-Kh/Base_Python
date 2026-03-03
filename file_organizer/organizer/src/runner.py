from typing import Optional, Any
from loguru import logger
from sys import exit

# Project modules
from .managers import RuleManager, ConfigManager, LogManager
from .core import Organizer
from .exceptions import OrganizerError


def runner(args: Optional[Any], config_path: Optional[str]) -> None:
    """
    Main entry point for the organizer.
    Loads config, sets up logging, creates managers and runs the organizer.
    """
    try:
        # 1. Load and merge configuration
        configs = ConfigManager(args=args, custom_cfg_path=config_path).configs

        # 2. Configure logging (this sets up Loguru globally)
        LogManager(config=configs.get('logger_cfg', {}))

        # 3. Create RuleManager and Organizer
        rule_manager = RuleManager(config=configs.get('rule_cfg', {}))
        organizer = Organizer(rule_manager=rule_manager, config=configs.get('core_cfg', {}))

        # 4. Run the organization
        organizer.organize()

    except OrganizerError as exc:
        logger.error(f"Organizer error: {exc}")
        exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        exit(0)
    except Exception as exc:
        logger.exception(f"Unexpected error: {exc}")
        exit(2)
