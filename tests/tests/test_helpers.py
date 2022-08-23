from unittest.mock import Mock

from blocks.models import HeaderBlock, TextBlock

from streamfield import helpers
from streamfield.registry import Registry

Header = Mock(
    pk=1,
    _meta=Mock(app_label="blocks", model_name="headerblock")
)


def test_get_streamblock_dict():
    data = helpers.get_streamblock_dict(Header)
    assert data == {
        "app_label": "blocks",
        "model_name": "headerblock",
        "pk": 1
    }


def test_get_streamblock_models():
    registry = Registry()
    registry.register(HeaderBlock)
    registry.register(TextBlock)

    blocks = list(helpers.get_streamblock_models(registry))
    assert len(blocks) == 2
    assert blocks == [HeaderBlock, TextBlock]
