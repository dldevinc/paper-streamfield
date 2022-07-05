from functools import lru_cache
from typing import List, Type

from django.apps import apps

from .models import StreamBlockModelMixin


@lru_cache
def get_streamblocks_models() -> List[Type[StreamBlockModelMixin]]:
    """
    Возвращает список моделей всех блоков.
    """
    return [
        model
        for model in apps.get_models()
        if issubclass(model, StreamBlockModelMixin) and not model._meta.abstract
    ]
