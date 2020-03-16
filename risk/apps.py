from django.apps import AppConfig


class RiskConfig(AppConfig):
    name = 'risk'

    def ready(self):
        import risk.signals
