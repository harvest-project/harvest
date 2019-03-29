import importlib
import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PluginMeta:
    def __init__(self, name):
        self.name = name
        self.module_path = 'plugins.{}'.format(self.name)
        self.app_config_name = ''.join(part.capitalize() for part in self.name.split('_')) + 'Config'
        self.app_config_path = '{}.apps.{}'.format(self.module_path, self.app_config_name)
        self.settings_module_path = '{}.settings'.format(self.module_path)
        self.urls_module_path = '{}.urls'.format(self.module_path)
        self.urls_prefix = 'api/plugins/{}/'.format(self.name)

    def __str__(self):
        return 'Plugin({})'.format(self.module_path)

    def import_settings(self):
        return importlib.import_module(self.settings_module_path)

    @classmethod
    def is_valid_name(cls, name):
        return (
                os.path.isdir(os.path.join(PLUGINS_ROOT, name)) and
                not name.startswith('_') and
                not name.startswith('.')
        )


PLUGINS_ROOT = os.path.join(BASE_DIR, 'plugins')


def get_plugins_list():
    return [PluginMeta(name) for name in os.listdir(PLUGINS_ROOT) if PluginMeta.is_valid_name(name)]


PLUGINS = get_plugins_list()

# Import all plugins' settings
for plugin in PLUGINS:
    try:
        plugin_module = plugin.import_settings()
    except ImportError:
        continue
    for attr in dir(plugin_module):
        if attr == attr.upper():
            value = getattr(plugin_module, attr)
            setattr(sys.modules[__name__], attr, value)
