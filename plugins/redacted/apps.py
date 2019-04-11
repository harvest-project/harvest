from django.apps import AppConfig


class RedactedConfig(AppConfig):
    name = 'plugins.redacted'

    def ready(self):
        super().ready()

        from trackers.registry import TrackerRegistry
        from plugins.redacted.tracker import RedactedTrackerPlugin
        TrackerRegistry.register(RedactedTrackerPlugin())
