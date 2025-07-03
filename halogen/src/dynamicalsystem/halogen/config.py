from dotenv import dotenv_values
from dataclasses import dataclass, field
from functools import lru_cache
from os import getenv
from os.path import join, isfile
from sys import exit
import logging

singleton = lru_cache(maxsize=1)

# Create a logger for this module
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Config:
    environment: str = field(init=False)
    data_folder: str = field(init=False)

    _namespace_file: str = field(init=False, repr=False)
    _package_file: str = field(init=False, repr=False)
    _namespace: str = field(init=False, repr=False)
    _package: str = field(init=False, repr=False)
    _prefix: str = field(init=False, repr=False)  # module name

    def __init__(self, context: str):
        """
        context: str - is assumed to be <namespace>.<package>.<module>
        In normal use just pass __name__ as the context so that you
        can assume that the config file is located at:
                ${<namespace>_FOLDER}/<namespace>/config/${ENVIRONMENT}[.package].env

        config will try to load a names file called ${ENVIRONMENT}.env before progressing
        to [.package].env. Values in the package file will override those in the
        namespace file where the variable is duplicated.

        Then, within the dotenv file, you can prefix each variable with the module name and
        get a Config object which is scoped to the module.

        Assumptions include that the environment variables are uppercase and underscore separated.

        The config object's attributes are lowercased and underscore separated.
        """

        self._parse_context(context)
        logger.info(f"Initializing config with context: {context}")

        root_folder = getenv(f"{self._namespace.upper()}_FOLDER")
        if not root_folder:
            logger.error(f"{self._namespace.upper()}_FOLDER not set")
            exit(f"{self._namespace.upper()}_FOLDER not set")
        logger.info(f"Root folder: {root_folder}")

        environment = getenv(f"{self._namespace.upper()}_ENVIRONMENT")
        if not environment:
            logger.error(f"{self._namespace.upper()}_ENVIRONMENT not set")
            exit(f"{self._namespace.upper()}_ENVIRONMENT not set")
        logger.info(f"Environment: {environment}")

        namespace_file = join(
            root_folder,
            self._namespace,
            "config",
            f"{self._namespace}.{environment}.env",
        )
        object.__setattr__(self, "_namespace_file", namespace_file)
        logger.info(f"Loading namespace config from: {namespace_file}")

        object.__setattr__(self, "environment", environment)

        self._package_attributes(root_folder)

        object.__setattr__(
            self,
            "data_folder",
            join(root_folder, self._namespace, "data"),
        )

        namespace_values = dotenv_values(self._namespace_file)
        logger.debug(f"Found {len(namespace_values)} variables in namespace config")
        for key, value in namespace_values.items():
            object.__setattr__(self, key.casefold(), value)
            logger.debug(f"Set namespace config: {key.casefold()}")
        
        # Set default values for test environment if not present
        if self.environment == "pytest":
            test_defaults = {
                "log_level": "DEBUG",
                "log_signal_identity": "test_identity",
                "log_signal_target": "test_target",
                "log_signal_url": "https://test.signal.url"
            }
            for key, default_value in test_defaults.items():
                if not hasattr(self, key):
                    object.__setattr__(self, key, default_value)
                    logger.debug(f"Set test default: {key} = {default_value}")

    def _package_attributes(self, root_folder: str):
        file = join(
            getenv(f"{self._namespace.upper()}_FOLDER"),
            self._namespace,
            "config",
            f"{self._package}.{self.environment}.env",
        )

        logger.debug(f"Checking for package config file: {file}")

        package_file = join(
            root_folder,
            self._namespace,
            "config",
            f"{self._package}.{self.environment}.env",
        )
        object.__setattr__(self, "_package_file", package_file)

        if isfile(file):
            logger.info(f"Loading package config from: {package_file}")

            package_values = dotenv_values(file)
            logger.debug(f"Found {len(package_values)} variables in package config")
            for key, value in package_values.items():
                if key.startswith(self._prefix.upper()):
                    attribute = key.removeprefix(self._prefix.upper() + "_")
                    object.__setattr__(self, attribute.casefold(), value)
                    logger.debug(f"Set package config: {attribute.casefold()} from {key}")
        else:
            logger.debug(f"Package config file not found: {file}")

    def _parse_context(self, context: str):
        _ = context.split(".")
        match len(_):
            case 3:
                object.__setattr__(self, "_namespace", _[0])
                object.__setattr__(self, "_package", _[1])
                object.__setattr__(self, "_prefix", _[2])
                return
            case 2:
                object.__setattr__(self, "_namespace", _[0])
                object.__setattr__(self, "_package", _[1])
                object.__setattr__(self, "_prefix", _[1])
                return
            case 1:
                object.__setattr__(self, "_namespace", _[0])
                object.__setattr__(self, "_package", _[0])
                object.__setattr__(self, "_prefix", _[0])
                return
            case _:
                logger.error(f"Invalid context: {context}")
                exit("Invalid context")

    def __str__(self):
        return self._namespace_file


@singleton
def config_instance(context: str):
    if not context:
        logger.error("No configuration context provided")
        exit("No configuration context provided")

    logger.info(f"Creating config instance for context: {context}")
    config = _Config(context)
    logger.debug(f"Config instance created with {len(dir(config))} attributes")
    logger.debug(f"Package: {config._package}")

    return config
