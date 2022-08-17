from unittest.mock import Mock

from streamfield.decorators import streamblock
from streamfield.registry import Registry

ProductModel = Mock(_meta=Mock(app_label="shop", model_name="product"))


def test_streamblock_decorator():
    registry = Registry()
    streamblock(name="decorated", _registry=registry)(ProductModel)

    assert len(registry) == 1
    assert ProductModel in registry
    assert registry[ProductModel] == {
        "name": "decorated"
    }
