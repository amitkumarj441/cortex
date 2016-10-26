from __future__ import unicode_literals

from django.apps import AppConfig


class CortexConfig(AppConfig):
    name = 'worldbrain.cortex'

    def ready(self):
        import worldbrain.cortex.signals.handlers  # NOQA
