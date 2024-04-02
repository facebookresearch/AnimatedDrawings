import os
import os.path as osp
import yaml
from typing import Any, IO
from easydict import EasyDict as edict
import json
import logging
from os import path as osp


class Loader(yaml.SafeLoader):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""

        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)


def construct_include(loader: Loader, node: yaml.Node) -> Any:
    """Include file referenced at node."""

    filename = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
    extension = os.path.splitext(filename)[1].lstrip('.')

    with open(filename, 'r') as f:
        if extension in ('yaml', 'yml'):
            return yaml.load(f, Loader)
        elif extension in ('json',):
            return json.load(f)
        else:
            return ''.join(f.readlines())


# load yaml file
def get_config(config_path):
    yaml.add_constructor('!include', construct_include, Loader)
    with open(config_path, 'r', encoding='utf-8') as stream:
        config = yaml.load(stream, Loader=Loader)
    # yaml dict -> common dict
    config = edict(config)
    _, config_filename = os.path.split(config_path)
    config_name, _ = os.path.splitext(config_filename)
    config.name = config_name
    return config


# common dict -> yaml file
def save_dict_to_yaml(obj, filename, mode='w'):
    with open(filename, mode) as f:
        yaml.dump(obj, f, default_flow_style=False)


if __name__ == '__main__':
    test_yaml_path = osp.join('../..', 'configs/default_config.yaml')
    cfg = get_config(test_yaml_path)
    print(cfg)