"""
Code based on solution https://gist.github.com/joshbode/569627ced3076931b02f
"""

from typing import Any, IO
import logging
import os
import yaml

from scanapi.errors import EmptyConfigFileError

logger = logging.getLogger(__name__)


class Loader(yaml.SafeLoader):
    """YAML/JSON Loader with `!include` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""

        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)


def construct_include(loader: Loader, node: yaml.Node) -> Any:
    """Include file referenced at node."""

    relative_path = os.path.join(loader._root, loader.construct_scalar(node))
    full_path = os.path.abspath(relative_path)

    with open(full_path, "r") as f:
        return yaml.load(f, Loader)


def load_config_file(file_path):
    """ Loads config file, checks extension of file - only .yaml, .yml and .json
    are supported. If non-empty file exists reads data and returns it
    """
    extension = os.path.splitext(file_path)[-1]

    if extension not in (".yaml", ".yml", ".json"):
        raise FileFormatNotSupportedError(extension, file_path)

    with open(file_path, "r") as stream:
        logger.info(f"Loading file {file_path}")
        data = yaml.load(stream, Loader)

        if not data:
            raise EmptyConfigFileError(file_path)

        return data


yaml.add_constructor("!include", construct_include, Loader)
