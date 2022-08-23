from typing import Any, Dict, Generator, Tuple

from django.apps import apps
from django.db.models import Model
from django.utils.module_loading import import_string

from .typing import BlockModel, RenderFuncCallable


def import_render_func(value: str) -> RenderFuncCallable:
    """
    Импортирует функцию отрисовки блока из строкового представления
    (пример: "app.views.render_header").
    """
    render_func = import_string(value)
    if not callable(render_func):
        raise ImportError("%s object is not callable" % value)
    return render_func


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


def get_streamblock_models(registry) -> Generator[Tuple[BlockModel, Dict], Any, None]:
    """
    Возвращает модели всех блоков с их параметрами.
    """
    for app_name, model_name in registry:
        model = apps.get_model(app_name, model_name)
        yield model
