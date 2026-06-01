"""[CLIENT-SPECIFIC] Load and validate client configuration.

Modify to load your specific client config.
"""
import os
import yaml
from pathlib import Path
from src.utils.logger_config import logger


def load_client_config(config_file: str = "config/client.config.yaml") -> dict:
    """Load YAML config with ENV variable substitution.

    Args:
        config_file: Path to config YAML file.

    Returns:
        Loaded and substituted config dict.
    """
    config_path = Path(config_file)

    if not config_path.exists():
        logger.warning(
            f"Config file not found: {config_file}. Using defaults."
        )
        return {
            "app": {"name": "Chatbot"},
            "prompts": {"system": "You are a helpful assistant."},
            "tools": [],
            "responses": {"media_not_supported": "Media not supported."},
            "external_apis": {},
            "flows": {},
        }

    try:
        with open(config_path) as f:
            config_str = f.read()

        # Substitute ENV vars like ${VAR_NAME}
        for key, value in os.environ.items():
            config_str = config_str.replace(f"${{{key}}}", value)

        config = yaml.safe_load(config_str)
        logger.info(f"Config loaded from {config_file}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise


try:
    CLIENT_CONFIG = load_client_config()
except Exception as e:
    logger.error(f"Config loading failed: {e}")
    CLIENT_CONFIG = {
        "app": {"name": "Chatbot"},
        "prompts": {"system": "You are a helpful assistant."},
        "tools": [],
        "responses": {"media_not_supported": "Media not supported."},
        "external_apis": {},
        "flows": {},
    }
