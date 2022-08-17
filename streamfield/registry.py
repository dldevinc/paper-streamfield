from typing import Dict, Tuple

from django.db.models.utils import make_model_tuple


class Registry:
    """
    Реестр моделей блоков.

    Каждому блоку в реестре соответствует произвольный словарь параметров.
    При многократной регистрации одной и той же модели с разным набором
    параметров - в реестре останется единственная запись с тем набором параметров,
    которые были указаны последними.
    """
    __slots__ = ("_registry",)

    def __init__(self):
        self._registry = {}  # type: Dict[Tuple[str, str]]

    def __iter__(self):
        return iter(sorted(self._registry))

    def __len__(self):
        return len(self._registry)

    def __getitem__(self, item):
        model_tuple = make_model_tuple(item)
        return self._registry[model_tuple]

    def __contains__(self, item):
        model_tuple = make_model_tuple(item)
        return model_tuple in self._registry

    def register(self, model, **options):
        model_tuple = make_model_tuple(model)
        self._registry[model_tuple] = options


registry = Registry()
