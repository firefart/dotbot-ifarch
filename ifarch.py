import platform
import os
import glob
from typing import List
import dotbot
from dotbot import Plugin
from dotbot.dispatcher import Dispatcher
from dotbot.plugins import Clean, Create, Link, Shell
from dotbot.util import module

class IfArch(dotbot.Plugin):
    _archs = [
        'aarch64',
        'arm64',
        'armv7l',
        'x86_64',
    ]

    def __init__(self, context):
        super().__init__(context)
        self._directives = [f"if{a}" for a in self._archs]

    def can_handle(self, directive):
        return directive in self._directives

    def handle(self, directive, data):
        if directive not in self._directives:
            raise ValueError(f"Cannot handle this directive {directive}")

        arch = platform.machine()
        if directive == 'if'+arch:
            self._log.debug(f"Matched arch {arch}")
            return self._run_internal(data)
        return True

    def _load_plugins(self) -> List[Plugin]:
        plugin_paths = self._context.options().plugins
        plugins = []
        for directory in self._context.options().plugin_dirs:
            for path in glob.glob(os.path.join(directory, "*.py")):
                plugin_paths.append(path)
        for path in plugin_paths:
            abspath = os.path.abspath(path)
            plugins.extend(module.load(abspath))
        if not self._context.options().disable_built_in_plugins:
            plugins.extend([Clean, Create, Link, Shell])
        return plugins

    def _run_internal(self, data):
        dispatcher = Dispatcher(
            self._context.base_directory(),
            only=self._context.options().only,
            skip=self._context.options().skip,
            options=self._context.options(),
            plugins=self._load_plugins(),
        )
        return dispatcher.dispatch(data)
