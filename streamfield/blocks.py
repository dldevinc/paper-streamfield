from typing import Dict
from uuid import uuid4

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .conf import DEFAULT_PROCESSOR
from .processors import BaseProcessor
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
        "pk": str(instance.pk),
        "visible": True
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


def get_model(value: Dict[str, str]) -> BlockModel:
    """
    Возвращает класс модели блока из словаря,
    созданного с помощью функции `to_dict()`.
    """
    return apps.get_model(value["model"])


def get_processor(model: BlockModel) -> BaseProcessor:
    """
    Возвращает экземпляр обработчика для указанной модели.
    """
    stream_meta = getattr(model, "StreamBlockMeta", None)
    if stream_meta is not None:
        processor = getattr(stream_meta, "processor", None) or DEFAULT_PROCESSOR
    else:
        processor = DEFAULT_PROCESSOR

    if isinstance(processor, str):
        processor = import_string(processor)

    if not isinstance(processor, type):
        raise ImproperlyConfigured("StreamBlock processor is not a class: %r" % processor)

    return processor(
        app_label=model._meta.app_label,
        model_name=model.__name__,
        **(stream_meta.__dict__ if stream_meta is not None else {})
    )
