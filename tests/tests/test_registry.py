from typing import Type, Union
from unittest.mock import Mock

from django.contrib.admin import AdminSite
from django.db.models import Model

from streamfield.registry import Registry

ProductModel = Mock(_meta=Mock(app_label="shop", model_name="product"))  # type: Union[Mock, Type[Model]]
ArticleModel = Mock(_meta=Mock(app_label="blog", model_name="article"))  # type: Union[Mock, Type[Model]]

MobileAdminSite = Mock(spec=AdminSite(name="mobile"))
MobileAdminSite.name = "mobile"


def test_inner_len():
    registry = Registry()
    assert len(registry._registry) == 0

    registry.register(ProductModel)
    assert len(registry["admin"]) == 1

    registry.register(ArticleModel, site=MobileAdminSite)
    assert len(registry["admin"]) == 1
    assert len(registry["mobile"]) == 1


def test_getitem():
    registry = Registry()
    registry.register(ProductModel)
    assert isinstance(registry["admin"], set)

    registry.register(ArticleModel, site=MobileAdminSite)
    assert isinstance(registry["mobile"], set)


def test_contains():
    registry = Registry()

    assert "admin" not in registry
    registry.register(ProductModel)
    assert "admin" in registry

    assert "mobile" not in registry
    registry.register(ArticleModel, site=MobileAdminSite)
    assert "mobile" in registry


def test_register():
    registry = Registry()
    registry.register(ProductModel)
    registry.register(ArticleModel, site=MobileAdminSite)

    assert registry["admin"] == {
        ("shop", "product"),
    }

    assert registry["mobile"] == {
        ("blog", "article"),
    }


def test_is_registered():
    registry = Registry()
    registry.register(ProductModel)
    registry.register(ArticleModel, site=MobileAdminSite)

    assert registry.is_registered(ProductModel)
    assert registry.is_registered(ArticleModel, site=MobileAdminSite)


def test_unregister():
    registry = Registry()
    registry.register(ProductModel)
    registry.register(ArticleModel, site=MobileAdminSite)

    assert registry.is_registered(ProductModel)
    registry.unregister(ProductModel)
    assert registry.is_registered(ProductModel) is False

    assert registry.is_registered(ArticleModel, site=MobileAdminSite)
    registry.unregister(ArticleModel, site=MobileAdminSite)
    assert registry.is_registered(ArticleModel, site=MobileAdminSite) is False


def test_double_register():
    registry = Registry()
    assert len(registry["admin"]) == 0

    registry.register(ProductModel)
    assert len(registry["admin"]) == 1

    registry.register(ProductModel)
    assert len(registry["admin"]) == 1
