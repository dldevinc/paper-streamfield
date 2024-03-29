from uuid import uuid4

import pytest
from blocks.models import HeaderBlock, TextBlock

from streamfield import exceptions, helpers


@pytest.mark.django_db
class TestRenderStream:
    def test_string_input(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        stream = '[{"uuid": "%s", "model": "blocks.headerblock", "pk": "1"}]' % uuid4()
        output = helpers.render_stream(stream)
        assert output == "<h1>Example header</h1>"

    def test_object_input(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        stream = [{
            "uuid": str(uuid4()),
            "model": "blocks.headerblock",
            "pk": "1"
        }]
        output = helpers.render_stream(stream)
        assert output == "<h1>Example header</h1>"

    def test_non_list_input(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        stream = '{"uuid": "%s", "model": "blocks.headerblock", "pk": "1"}' % uuid4()
        with pytest.raises(exceptions.InvalidStreamTypeError):
            helpers.render_stream(stream)

    def test_invalid_block(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )

        stream = [{
            "uuid": str(uuid4()),
            "model": "blocks.headerblock",
            "pk": "1"
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.textblock",
            "pk": 1  # invalid type
        }]

        with pytest.raises(exceptions.InvalidStreamBlockError):
            helpers.render_stream(stream)

    def test_skipping_non_existent_block(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )

        stream = [{
            "uuid": str(uuid4()),
            "model": "blocks.headerblock",
            "pk": "1"
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.textblock",
            "pk": "999"
        }]

        output = helpers.render_stream(stream)
        assert output == "<h1>Example header</h1>"

    def test_visibility(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )
        TextBlock.objects.create(
            pk=2,
            text="Another text"
        )

        stream = [{
            "uuid": str(uuid4()),
            "model": "blocks.headerblock",
            "pk": "1",
            "visible": True
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.textblock",
            "pk": "1",
            "visible": False
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.textblock",
            "pk": "2",
            "visible": True
        }]

        output = helpers.render_stream(stream)
        assert output == "<h1>Example header</h1>\n<div><p>Another text</p></div>"


@pytest.mark.django_db
class TestRenderBlock:
    def test_rendering(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        output = helpers.render_block({
            "model": "blocks.HeaderBlock",
            "pk": 1
        })
        assert output == "<h1>Example header</h1>"

    def test_parent_context(self):
        TextBlock.objects.create(
            pk=1,
            text="Dark text"
        )

        output = helpers.render_block({
            "model": "blocks.TextBlock",
            "pk": 1
        }, {
            "theme": "dark"
        })
        assert output == '<div class="text--dark"><p>Dark text</p></div>'
