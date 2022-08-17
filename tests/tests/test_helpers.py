from unittest.mock import Mock
from blocks.models import HeaderBlock, ImageBlock, TextBlock

from streamfield import helpers

Product = Mock(
    pk=1,
    _meta=Mock(app_label="shop", model_name="product")
)


def test_get_streamblock_models():
    blocks = list(helpers.get_streamblock_models())
    assert len(blocks) == 3
    assert [pair[0] for pair in blocks] == [
        HeaderBlock,
        ImageBlock,
        TextBlock
    ]


def test_get_streamblock_dict():
    data = helpers.get_streamblock_dict(Product)
    assert data == {
        "app_label": "shop",
        "model_name": "product",
        "pk": 1
    }
