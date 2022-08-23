from django.apps import apps

from streamfield.models import StreamBlockMetaClass
from streamfield.registry import Registry
from streamfield.registry import registry as default_registry


def autodiscover_block_models(registry: Registry = None):
    if registry is None:
        registry = default_registry

    for model in apps.get_models():
        if isinstance(model, StreamBlockMetaClass):
            registry.register(model)
