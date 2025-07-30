from .config_parser import Config
from .config_writer import write_config
from types import SimpleNamespace
from typing import Optional, List

__all__ = ["parse_config", "write_config"]

def parse_config(config_paths: Optional[List[str]] = None) -> SimpleNamespace:
    """
    Retrieves the application configuration, including both YAML, JSON, TOM and .env content.

    :param config_paths: Optional list of paths to project specific config files
    :return: A namespace object with config and env values accessible via dot notation.
    """
    if config_paths:
        Config().reload(config_paths)

    return Config().get()