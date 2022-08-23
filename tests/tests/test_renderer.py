from typing import Type, Union
from unittest.mock import Mock

import pytest
from blocks.models import HeaderBlock
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.template import TemplateDoesNotExist

from streamfield.models import Options
from streamfield.renderer import TemplateRenderer

DummyModel = Mock(spec=[])  # type: Union[Mock, Type[Model]]


def test_resolve_template_with_string():
    renderer = TemplateRenderer(DummyModel)
    template = renderer.resolve_template("blocks/header.html")
    assert template.template.name == "blocks/header.html"


def test_resolve_template_with_tuple():
    renderer = TemplateRenderer(DummyModel)
    template = renderer.resolve_template(
        ("blocks/missing.html", "blocks/header.html")
    )
    assert template.template.name == "blocks/header.html"


def test_resolve_template_fail():
    renderer = TemplateRenderer(DummyModel)
    with pytest.raises(TemplateDoesNotExist):
        renderer.resolve_template("blocks/missing.html")


def test_render_template():
    renderer = TemplateRenderer(Mock(  # noqa
        _stream_meta=Options(
            template="blocks/header.html"
        )
    ))
    instance = HeaderBlock(text="Example header")
    assert renderer(instance) == "<h1>Example header</h1>"


def test_render_undefined_template():
    renderer = TemplateRenderer(DummyModel)
    instance = HeaderBlock(text="Example header")
    with pytest.raises(ImproperlyConfigured):
        assert renderer(instance)


def test_render_missing_template():
    renderer = TemplateRenderer(Mock(  # noqa
        _stream_meta=Options(
            template="blocks/missing.html"
        )
    ))
    instance = HeaderBlock(text="Example header")
    with pytest.raises(TemplateDoesNotExist):
        assert renderer(instance)
