from typing import Optional, Any

# Project modules
from .managers import RuleManager, ConfigManager, LogManager
from .core import Organizer
from .exceptions import OrganizerError


# Main core runner
def runner(args: Optional[Any], config_path: Optional[str]) -> None:
    configs = ConfigManager(args=args, custom_cfg_path=config_path).configs

    logger = LogManager(config=configs.get('logger_cfg', {}))
    
    try:
        rule_manager = RuleManager(config=configs.get('rule_cfg', {}))
        organizer = Organizer(rule_manager=rule_manager, config=configs.get('core_cfg', {}))
        organizer.organize()
    except OrganizerError as exc:


    