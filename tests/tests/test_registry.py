from unittest.mock import Mock

import pytest

from streamfield.registry import Registry

ProductModel = Mock(_meta=Mock(app_label="shop", model_name="product"))
ArticleModel = Mock(_meta=Mock(app_label="blog", model_name="article"))


def test_getitem():
    registry = Registry()
    registry.register(ProductModel)
    assert registry[ProductModel] is registry[("shop", "product")] is registry["shop.product"]
    assert type(registry[ProductModel]) is dict


def test_getitem_fail():
    registry = Registry()
    registry.register(ProductModel)
    with pytest.raises(LookupError):
        registry[ArticleModel]  # noqa


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


def test_default_options():
    registry = Registry()
    registry.register(ProductModel)
    assert registry[ProductModel] == {}


def test_custom_options():
    registry = Registry()
    registry.register(ProductModel, name="example", force=True)
    assert ("shop", "product") in registry
    assert registry[ProductModel] == {
        "name": "example",
        "force": True
    }


def test_duplicate_register():
    registry = Registry()
    registry.register(ProductModel, name="yellow", index=1)
    registry.register(ProductModel, name="green", alias="apple")

    assert len(registry) == 1
    assert registry[ProductModel] == {
        "name": "green",
        "alias": "apple"
    }
