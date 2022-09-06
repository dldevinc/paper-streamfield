from typing import Type, Union
from unittest.mock import Mock

import pytest
from blocks.models import HeaderBlock
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.template import TemplateDoesNotExist

from streamfield.renderer import render_template, resolve_template

DummyModel = Mock(spec=[])  # type: Union[Mock, Type[Model]]


def test_resolve_template_with_string():
    template = resolve_template("blocks/header.html")
    assert template.template.name == "blocks/header.html"


def test_resolve_template_with_tuple():
    template = resolve_template(
        ("blocks/missing.html", "blocks/header.html")
    )
    assert template.template.name == "blocks/header.html"


def test_resolve_template_fail():
    with pytest.raises(TemplateDoesNotExist):
        resolve_template("blocks/missing.html")


def test_render_template():
    instance = HeaderBlock(text="Example header")
    assert render_template(instance) == "<h1>Example header</h1>"


def test_render_undefined_template():
    with pytest.raises(ImproperlyConfigured):
        assert render_template(Mock(
            spec=["text", "_meta"],
            _meta=Mock(
                app_label="blocks",
                model_name="headerblock",
            ),
            text="Example header"
        ))


def test_render_missing_template():
    with pytest.raises(TemplateDoesNotExist):
        assert render_template(Mock(
            spec=["block_template", "_meta"],
            _meta=Mock(
                app_label="blocks",
                model_name="headerblock",
            ),
            block_template="blocks/missing.html"
        ))
