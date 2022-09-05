from collections import defaultdict
from typing import Dict, Set, Tuple

from django.contrib.admin.sites import site as default_site
from django.db.models.utils import make_model_tuple


class Registry:
    """
    Реестр моделей блоков.
    """
    __slots__ = ("_registry",)

    def __init__(self):
        self._registry = defaultdict(set)  # type: Dict[str, Set[Tuple[str, str]]]

    def __getitem__(self, site_name: str):
        return self._registry[site_name]

    def __contains__(self, site_name: str):
        return site_name in self._registry

    def register(self, model, site=None):
        admin_site = site or default_site
        model_tuple = make_model_tuple(model)
        self._registry[admin_site.name].add(model_tuple)

    def unregister(self, model, site=None):
        admin_site = site or default_site
        model_tuple = make_model_tuple(model)
        self._registry[admin_site.name].remove(model_tuple)

    def is_registered(self, model, site=None):
        admin_site = site or default_site
        model_tuple = make_model_tuple(model)
        return model_tuple in self._registry[admin_site.name]


registry = Registry()
