from typing import Set, Tuple

from django.db.models.utils import make_model_tuple


class Registry:
    """
    Реестр моделей блоков.
    """
    __slots__ = ("_registry",)

    def __init__(self):
        self._registry = set()  # type: Set[Tuple[str, str]]

    def __iter__(self):
        return iter(sorted(self._registry))

    def __len__(self):
        return len(self._registry)

    def __contains__(self, item):
        model_tuple = make_model_tuple(item)
        return model_tuple in self._registry

    def register(self, model):
        model_tuple = make_model_tuple(model)
        self._registry.add(model_tuple)

    def unregister(self, model):
        model_tuple = make_model_tuple(model)
        self._registry.remove(model_tuple)


registry = Registry()
