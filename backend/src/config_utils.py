import os
from pathlib import Path
import yaml

def load_config():
    """
    Load configuration from config.yml file
    """
    config_path = Path(__file__).parent.parent.parent / "config.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def get_config_value(section, key, default=None):
    """
    Get a specific value from the config file
    
    Args:
        section: The section in the config file (e.g., 'backend', 'frontend')
        key: The key within the section
        default: Default value if the key is not found
    
    Returns:
        The value from the config or the default
    """
    config = load_config()
    
    if section in config and key in config[section]:
        return config[section][key]
    
    return default