from rest_framework.exceptions import APIException


class PluginMissingException(APIException):
    status_code = 400

    def __init__(self, name, action):
        super().__init__('Missing plugin {} to perform {}.'.format(name, action))


class DuplicatePluginException(Exception):
    def __init__(self, name, *args, **kwargs):
        super().__init__('Trying to register a duplicate plugin {}.'.format(name), *args, **kwargs)


class InvalidPluginException(Exception):
    def __init__(self, name, *args, **kwargs):
        super().__init__('Trying to register a duplicate plugin {}.'.format(name), *args, **kwargs)


class PluginRegistry:
    def __init__(self):
        self._plugins = {}

    def register_plugin(self, plugin):
        if plugin.name in self._plugins:
            raise DuplicatePluginException(plugin.name)
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name, action=None):
        plugin = self._plugins.get(name)
        if plugin is None:
            raise PluginMissingException(name, action)
        return plugin

    def get_plugins(self):
        return list(self._plugins.values())


TrackerRegistry = PluginRegistry()
