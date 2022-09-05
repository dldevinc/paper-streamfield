from typing import Dict, Optional, Type, cast
from uuid import uuid4

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest
from django.utils.module_loading import import_string

from . import conf
from .logging import logger
from .models import StreamBlockMetaClass
from .renderer import BaseRenderer
from .typing import BlockInstance


def to_dict(instance: BlockInstance) -> Dict[str, str]:
    """
    Сериализация блока для JSON.

    Для облегчения управления блоками на фронтенде
    в выходной словарь добавляется значение `uuid`.
    Оно позволяет задать двустороннее соответствие
    между JSON-объектом и DOM-элементом.
    """
    return {
        "uuid": str(uuid4()),
        "app_label": instance._meta.app_label,
        "model_name": instance._meta.model_name,
        "pk": str(instance.pk)
    }


def from_dict(value: Dict[str, str]) -> Optional[BlockInstance]:
    """
    Возвращает экземпляр блока из словаря,
    созданного с помощью функции `to_dict()`.
    """
    try:
        model = apps.get_model(
            value["app_label"],
            value["model_name"]
        )
    except LookupError:
        logger.warning(
            "Model '%(app_label)s.%(model_name)s' not found."
            % value
        )
        return

    if not isinstance(model, StreamBlockMetaClass):
        logger.warning(
            "Model '%(app_label)s.%(model_name)s' is not a stream block."
            % value
        )
        return

    instance = model._base_manager.filter(pk=value["pk"]).first()
    if instance is None:
        logger.warning(
            "Object '%(app_label)s.%(model_name)s' with primary key '%(pk)s' does not exist."
            % value
        )
        return

    return instance


def render(block: BlockInstance, extra_context: Dict = None, request: WSGIRequest = None) -> str:
    """
    Отрисовка экземпляра блока.
    """
    renderer = getattr(block._stream_meta, "renderer", conf.DEFAULT_RENDERER)
    if isinstance(renderer, str):
        renderer_name = renderer
        renderer = import_string(renderer_name)
        if not callable(renderer):
            raise ImportError("%s object is not callable" % renderer_name)

    if isinstance(renderer, type):
        renderer = cast(Type[BaseRenderer], renderer)
        renderer = renderer(type(block))

    return renderer(block, extra_context, request=request)
