from typing import Any, Dict, Generator, Tuple, Type

from django.apps import apps
from django.db.models import Model

from .registry import registry


def get_streamblock_models() -> Generator[Tuple[Type[Model], Dict], Any, None]:
    """
    Возвращает модели всех блоков с их параметрами.
    """
    for app_name, model_name in registry:
        model = apps.get_model(app_name, model_name)
        options = registry[(app_name, model_name)]
        yield model, options


def get_streamblock_dict(instance: Model):
    """
    Возвращает JSON-сериализуемый словарь,
    которым блок будет представлен в БД.
    """
    return {
        "app_label": instance._meta.app_label,
        "model_name": instance._meta.model_name,
        "pk": instance.pk
    }
