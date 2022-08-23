from unittest.mock import Mock

import pytest
from blocks.models import HeaderBlock, TextBlock

from streamfield import helpers
from streamfield.registry import Registry

Header = Mock(
    pk=1,
    _meta=Mock(app_label="blocks", model_name="headerblock")
)


def test_get_block_models():
    registry = Registry()
    registry.register(HeaderBlock)
    registry.register(TextBlock)

    blocks = list(helpers.get_block_models(registry))
    assert len(blocks) == 2
    assert blocks == [HeaderBlock, TextBlock]


def test_get_block_dict():
    data = helpers.get_block_dict(Header)
    assert data == {
        "app_label": "blocks",
        "model_name": "headerblock",
        "pk": 1
    }


@pytest.mark.django_db
def test_get_stream_blocks():
    header = HeaderBlock.objects.create(
        pk=1,
        text="Example header"
    )
    text = TextBlock.objects.create(
        pk=1,
        text="Example text"
    )

    blocks = helpers.get_stream_blocks([
        {
            "app_label": "blocks",
            "model_name": "headerblock",
            "pk": 1
        },
        {
            "app_label": "blocks",
            "model_name": "textblock",
            "pk": 1
        },
        {  # missing blocks are skipped
            "app_label": "blocks",
            "model_name": "missing",
            "pk": 999
        }
    ])

    assert list(blocks) == [header, text]


def test_render_block():
    block = HeaderBlock(
        text="Example header"
    )
    assert helpers.render_block(block) == "<h1>Example header</h1>"
