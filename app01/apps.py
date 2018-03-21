from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class App01Config(AppConfig):
    name = 'app01'

    def ready(self):
        autodiscover_modules('stark')

