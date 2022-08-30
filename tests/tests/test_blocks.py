from unittest.mock import Mock

import pytest
from blocks.models import HeaderBlock, TextBlock

from streamfield import blocks
from streamfield.registry import Registry

Header = Mock(
    pk=1,
    _meta=Mock(app_label="blocks", model_name="headerblock")
)


def test_get_models():
    registry = Registry()
    registry.register(HeaderBlock)
    registry.register(TextBlock)

    models = list(blocks.get_models(registry))
    assert len(models) == 2
    assert models == [HeaderBlock, TextBlock]


def test_to_dict():
    data = blocks.to_dict(Header)
    assert "uuid" in data

    data.pop("uuid")
    assert data == {
        "app_label": "blocks",
        "model_name": "headerblock",
        "pk": "1"
    }


@pytest.mark.django_db
def test_from_dict():
    HeaderBlock.objects.create(
        pk=1,
        text="Example header"
    )

    assert blocks.from_dict({
        "app_label": "unknown",
        "model_name": "headerblock",
        "pk": "1"
    }) is None

    assert blocks.from_dict({
        "app_label": "blocks",
        "model_name": "headerblock",
        "pk": "999"
    }) is None

    block = blocks.from_dict({
        "app_label": "blocks",
        "model_name": "headerblock",
        "pk": "1"
    })
    assert block is not None


def test_render():
    block = HeaderBlock(
        text="Example header"
    )
    assert blocks.render(block) == "<h1>Example header</h1>"
