#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
import os.path as p
import importlib
from exceptions import DoNotImportException
from util import TCodes
from apiconfig import config


def load_folder(folder: str):
    modules = []
    for root, dirnames, files in os.walk(folder, topdown=True):
        for dirname in dirnames:
            if dirname.startswith("_"):
                dirnames.remove(dirname)
            if p.isfile(p.join(root, dirname, "__init__.py")):
                module_name = '.'.join([*root.split(os.sep), dirname])
                try:
                    module = importlib.import_module(module_name)
                except DoNotImportException:
                    print(f"{TCodes.FG_YELLOW}Disabled: {module_name}{TCodes.RESTORE_FG}")
                else:
                    modules.append(module)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext != ".py":
                continue
            module_name = '.'.join([*root.split(os.sep), name])
            try:
                module = importlib.import_module(module_name)
            except DoNotImportException:
                print(f"{TCodes.FG_YELLOW}Disabled: {module_name}{TCodes.RESTORE_FG}")
            else:
                modules.append(module)
    return modules


def load_plugins():
    plugins = {}
    for name in os.listdir("plugins"):
        if name.startswith("_"):
            continue
        if config.getboolean("plugins", name, fallback=True) is False:
            continue
        try:
            plugin = importlib.import_module(f"plugins.{name}")
        except DoNotImportException:
            print(f"{TCodes.FG_YELLOW}Disabled Plugin: {name}{TCodes.RESTORE_FG}")
        else:
            print(f"{TCodes.FG_GREEN}Loaded Plugin: {name}{TCodes.RESTORE_FG}")
            plugins[name] = plugin
    return plugins
