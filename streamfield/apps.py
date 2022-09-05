from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    name = "streamfield"
    verbose_name = _("Streamfield")
