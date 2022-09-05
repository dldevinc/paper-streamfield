from django.contrib import admin
from django.contrib.admin.sites import site as default_site

from ..registry import registry


class ModelAdmin(admin.ModelAdmin):
    """
    Базовый класс интерфейса администратора для блоков.
    """
    popup_response_template = "streamfield/popup_response.html"


def register(*models, site=None):
    """
    Алиас для декоратора `registry.register()`.

    Позволяет использовать следующий синтаксис:
        # admin.py

        from streamfield import admin

        @admin.register(MyStreamBlock)
        class MyStreamBlockModelAdmin(admin.ModelAdmin):
            ...
    """
    admin_site = site or default_site

    for model in models:
        registry.register(model, site=admin_site)

    return admin.register(*models, site=admin_site)
