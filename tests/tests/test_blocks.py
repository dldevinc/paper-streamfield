import pytest
from django.core.exceptions import ObjectDoesNotExist

from blocks.models import HeaderBlock

from streamfield import blocks


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
            "pk": "1"
        }


class TestIsValid:
    def test_valid(self):
        assert blocks.is_valid({
            "uuid": "1234-5678",
            "model": "blocks.header",
            "pk": "1",
        }) is True

    def test_missing_required_key(self):
        assert blocks.is_valid({
            "uuid": "123",
            "model": "blocks.header",
            "id": "6"
        }) is False

    def test_non_string_values(self):
        assert blocks.is_valid({
            "uuid": "1234-5678",
            "model": "blocks.header",
            "pk": 1,
        }) is False

        assert blocks.is_valid({
            "uuid": "1234-5678",
            "model": "blocks.header",
            "pk": "1",
            "non-required-key": 42,  # allowed
        }) is True


@pytest.mark.django_db
class TestFromDict:
    def test_invalid_model(self):
        with pytest.raises(LookupError):
            blocks.from_dict({
                "model": "unknown.headerblock",
                "pk": "1"
            })

    def test_object_does_not_exists(self):
        with pytest.raises(ObjectDoesNotExist):
            blocks.from_dict({
                "model": "blocks.headerblock",
                "pk": "1"
            })

    def test_valid(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        block = blocks.from_dict({
            "model": "blocks.headerblock",
            "pk": "1"
        })
        assert block is not None


class TestRender:
    def test_header(self):
        block = HeaderBlock(
            text="Example header"
        )
        assert blocks.render(block) == "<h1>Example header</h1>"
