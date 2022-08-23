from typing import Type, Union
from unittest.mock import Mock

from django.db.models import Model

from streamfield.registry import Registry

ProductModel = Mock(_meta=Mock(app_label="shop", model_name="product"))  # type: Union[Mock, Type[Model]]
ArticleModel = Mock(_meta=Mock(app_label="blog", model_name="article"))  # type: Union[Mock, Type[Model]]


def test_len():
    registry = Registry()
    assert len(registry) == 0

    registry.register(ProductModel)
    assert len(registry) == 1

    registry.register(ArticleModel)
    assert len(registry) == 2


def test_contains():
    registry = Registry()
    registry.register(ProductModel)
    assert ProductModel in registry
    assert ("shop", "product") in registry
    assert "shop.product" in registry


def test_contains_fail():
    registry = Registry()
    registry.register(ProductModel)
    assert ArticleModel not in registry
    assert "blog.article" not in registry


def test_unregister():
    registry = Registry()

    registry.register(ProductModel)
    assert len(registry) == 1
    assert ProductModel in registry

    registry.unregister(ProductModel)
    assert len(registry) == 0
    assert ProductModel not in registry


def test_duplicate_register():
    registry = Registry()
    assert len(registry) == 0

    registry.register(ProductModel)
    assert len(registry) == 1

    registry.register(ProductModel)
    assert len(registry) == 1
