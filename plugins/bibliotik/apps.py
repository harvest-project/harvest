from django.apps import AppConfig


class BibliotikConfig(AppConfig):
    name = 'plugins.bibliotik'

    def ready(self):
        super().ready()

        from trackers.registry import TrackerRegistry
        from plugins.bibliotik.tracker import BibliotikTrackerPlugin
        TrackerRegistry.register_plugin(BibliotikTrackerPlugin())
