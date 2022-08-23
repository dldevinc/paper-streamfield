from blocks.models import HeaderBlock, TextBlock, ImageBlock

from streamfield.autodiscover import autodiscover_block_models
from streamfield.registry import Registry


def test_autodiscover():
    registry = Registry()
    assert len(registry) == 0

    autodiscover_block_models(registry)
    assert len(registry) == 3
    assert HeaderBlock in registry
    assert TextBlock in registry
    assert ImageBlock in registry
