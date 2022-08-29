from typing import Any, Dict, Generator, Optional, Tuple, Type, cast

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest

from . import conf, utils
from .logging import logger
from .models import StreamBlockMetaClass
from .renderer import BaseRenderer
from .typing import BlockInstance, BlockModel


def get_models(registry) -> Generator[Tuple[BlockModel, Dict], Any, None]:
    """
    Возвращает модели всех блоков.
    """
    for app_name, model_name in registry:
        model = apps.get_model(app_name, model_name)
        yield model


def to_dict(instance: BlockInstance) -> Dict[str, str]:
    """
    Сериализация блока для JSON.
    """
    return {
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
    Отрисовка блока.
    """
    renderer = getattr(block._stream_meta, "renderer", conf.DEFAULT_RENDERER)
    if isinstance(renderer, str):
        renderer = utils.import_render_func(renderer)

    if isinstance(renderer, type):
        renderer = cast(Type[BaseRenderer], renderer)
        renderer = renderer(type(block))

    return renderer(block, extra_context, request=request)
