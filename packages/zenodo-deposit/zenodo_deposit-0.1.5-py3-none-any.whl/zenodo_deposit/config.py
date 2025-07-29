import tomllib as toml
import os
from functools import lru_cache
from typing import Dict
import logging

logger = logging.getLogger(__name__)

default_zenodo: Dict[str, str] = {
    "ZENODO_ACCESS_TOKEN": "Change me",
    "ZENODO_SANDBOX_ACCESS_TOKEN": "Change me",
}


settings_name = ".zenodo-deposit-settings.toml"


def first_file_that_exists(files):
    for file in files:
        if os.path.exists(file):
            return file
    return None


def read_config_file(file: str = None) -> Dict[str, Dict[str, str]]:
    """
    Read the config file, if given, else look in the standard locations
    will throw an error if the config file is not found, or it is invalid TOML
    """
    if file:
        logger.info(f"Reading config file: {file}")
        with open(file, "rb") as f:
            return toml.load(f)
    else:
        first_config = first_file_that_exists(
            [
                settings_name,
                os.path.expanduser(f"~/{settings_name}"),
            ]
        )
        if first_config:
            logger.info(f"Reading config file: {first_config}")
            with open(first_config, "rb") as f:
                return toml.load(f)
    return {"zenodo": default_zenodo}


@lru_cache(maxsize=32)
def config_section(
    config_file=None,
    section: str = "zenodo",
) -> Dict[str, str]:
    """
    Read a specific section from the configuration file, updating it with environment variables
    """
    config = read_config_file(config_file)
    config_section = config.get(section)
    if not config_section:
        raise ValueError(f"Section {section} not found in the configuration file")

    for key in config_section.keys():
        if key in os.environ:
            config_section[key] = os.environ[key]
    return config_section


def zenodo_config(config_file=None) -> Dict[str, str]:
    """
    Read the Zenodo configuration from the file (access keys)
    """
    return config_section(config_file, "zenodo")


def validate_zenodo_config(config: Dict[str, str], use_sandbox: bool = False) -> bool:
    """
    Validate the configuration.
    1. Ensure that the ZENODO_ACCESS_TOKEN or the ZENODO_SANDBOX_ACCESS_TOKEN is set
    to something other than the default value.
    """
    check1 = config.get("ZENODO_ACCESS_TOKEN") and (
        config["ZENODO_ACCESS_TOKEN"] != default_zenodo["ZENODO_ACCESS_TOKEN"]
    )
    check2 = config.get("ZENODO_SANDBOX_ACCESS_TOKEN") and (
        config["ZENODO_SANDBOX_ACCESS_TOKEN"]
        != default_zenodo["ZENODO_SANDBOX_ACCESS_TOKEN"]
    )
    logger.debug(f"Config: {config}")
    logger.debug(f"Check1: {check1}")
    logger.debug(f"Check2: {check2}")
    if not use_sandbox and not check1:
        raise ValueError("ZENODO_ACCESS_TOKEN is not set in production environment")
    if use_sandbox and not check2:
        raise ValueError(
            "ZENODO_SANDBOX_ACCESS_TOKEN is not set, sandbox being used. Config: "
            + str(config)
        )
    return True
