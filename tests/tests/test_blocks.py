import pytest
from blocks.models import *

from streamfield import blocks
from streamfield.processors import DefaultProcessor

from .mock import get_mock


class TestToDict:
    def test_header(self):
        header = HeaderBlock(
            pk=1,
            text="Example header"
        )

        data = blocks.to_dict(header)

        assert "uuid" in data
        data.pop("uuid")

        assert data == {
            "model": "blocks.headerblock",
            "pk": "1",
            "visible": True
        }


class TestIsValid:
    def test_valid(self):
        assert blocks.is_valid({
            "uuid": "1234-5678",
            "model": "blocks.header",
            "pk": "1",
            "visible": True
        }) is True

    def test_missing_required_key(self):
        assert blocks.is_valid({
            "uuid": "123",
            "model": "blocks.header",
            "id": "6",  # <---
            "visible": True
        }) is False

    def test_non_string_required_values(self):
        assert blocks.is_valid({
            "uuid": "1234-5678",
            "model": "blocks.header",
            "pk": 1,  # <---
            "visible": True
        }) is False

        assert blocks.is_valid({
            "uuid": "1234-5678",
            "model": "blocks.header",
            "pk": "1",
            "non-required-key": 42,  # allowed
            "visible": True
        }) is True


class TestGetModel:
    def test_valid_model(self):
        assert blocks.get_model({
            "model": "blocks.headerblock",
        }) is HeaderBlock

    def test_invalid_model(self):
        with pytest.raises(LookupError):
            blocks.get_model({
                "model": "unknown.headerblock",
                "pk": "1"
            })


class TestGetProcessor:
    def test_default_processor(self):
        processor = blocks.get_processor(HeaderBlock)
        assert isinstance(processor, DefaultProcessor)

    def test_processor_options(self):
        processor = blocks.get_processor(TextBlock)
        assert processor.get_template_names(get_mock()) == "blocks/text.html"
