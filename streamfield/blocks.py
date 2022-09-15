from typing import Dict
from uuid import uuid4

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest
from django.utils.module_loading import import_string

from . import conf
from .typing import BlockInstance, BlockModel


def to_dict(instance: BlockInstance) -> Dict[str, str]:
    """
    Сериализация блока для JSON.

    Для облегчения управления блоками на фронтенде
    в выходной словарь добавляется значение `uuid`.
    Оно позволяет задать двустороннее соответствие
    между JSON-объектом и DOM-элементом.
    """
    opts = instance._meta
    return {
        "uuid": str(uuid4()),
        "model": f"{opts.app_label}.{opts.model_name}",
        "pk": str(instance.pk)
    }


def is_valid(value: Dict[str, str]) -> bool:
    """
    Проверяет корректность словаря, представляющего блок.
    """
    if not isinstance(value, dict):
        return False

    required_keys = {"uuid", "model", "pk"}
    if required_keys.difference(value.keys()):
        return False

    if not all(isinstance(value[key], str) for key in required_keys):
        return False

    return True


def from_dict(value: Dict[str, str]) -> BlockInstance:
    """
    Возвращает экземпляр блока из словаря,
    созданного с помощью функции `to_dict()`.
    """
    model = apps.get_model(value["model"])  # type: BlockModel
    return model._base_manager.get(pk=value["pk"])


def render(block: BlockInstance, extra_context: Dict = None, request: WSGIRequest = None) -> str:
    """
    Отрисовка экземпляра блока.
    """
    renderer = getattr(block, "block_renderer", conf.DEFAULT_RENDERER)
    if isinstance(renderer, str):
        renderer_name = renderer
        renderer = import_string(renderer_name)
        if not callable(renderer):
            raise ImportError("%s object is not callable" % renderer_name)

    if isinstance(renderer, type):
        renderer = renderer()

    return renderer(block, extra_context, request=request)
