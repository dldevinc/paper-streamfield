from typing import Dict
from uuid import uuid4

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest

from .options import get_block_opts
from .typing import BlockInstance


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
    model = apps.get_model(value["model"])
    return model._base_manager.get(pk=value["pk"])


def render(block: BlockInstance, context: Dict = None, request: WSGIRequest = None) -> str:
    """
    Отрисовка экземпляра блока.
    """
    opts = get_block_opts(block)
    return opts.renderer(block, request=request, **(context or {}))
