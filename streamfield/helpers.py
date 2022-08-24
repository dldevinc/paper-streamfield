from typing import Any, Dict, Generator, Sequence, Tuple, Type, cast

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction, models
from django.db.models import Model

from . import conf, utils
from .field.models import StreamField
from .logging import logger
from .renderer import BaseRenderer
from .typing import BlockInstance, BlockModel


def get_block_models(registry) -> Generator[Tuple[BlockModel, Dict], Any, None]:
    """
    Возвращает модели всех блоков с их параметрами.
    """
    for app_name, model_name in registry:
        model = apps.get_model(app_name, model_name)
        yield model


def get_block_dict(instance: Model) -> Dict:
    """
    Возвращает JSON-сериализуемый словарь,
    которым блок будет представлен в БД.
    """
    return {
        "app_label": instance._meta.app_label,
        "model_name": instance._meta.model_name,
        "pk": str(instance.pk)
    }


def get_stream_blocks(stream: Sequence) -> Generator[BlockInstance, Any, None]:
    """
    Парсит JSON и возвращает экземпляры блоков.
    """
    for record in stream:
        try:
            model = apps.get_model(
                record["app_label"],
                record["model_name"]
            )
        except LookupError as exc:
            logger.warning(exc)
            continue

        instance = model._base_manager.filter(pk=record["pk"]).first()
        if instance is None:
            logger.warning(
                "Object '%(app_label)s.%(model_name)s' with primary key '%(pk)s' does not exist."
                % record
            )
            continue

        yield instance


def render_block(block: BlockInstance, extra_context: Dict = None, request: WSGIRequest = None) -> str:
    renderer = getattr(block._stream_meta, "renderer", conf.DEFAULT_RENDERER)
    if isinstance(renderer, str):
        renderer = utils.import_render_func(renderer)

    if isinstance(renderer, type):
        renderer = cast(Type[BaseRenderer], renderer)
        renderer = renderer(type(block))

    return renderer(block, extra_context, request=request)
