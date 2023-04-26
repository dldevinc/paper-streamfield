from typing import Type, Union
from unittest.mock import Mock

import pytest
from blocks.models import HeaderBlock
from django.db.models import Model
from django.template import TemplateDoesNotExist

from streamfield.renderer import render_template, resolve_template

DummyModel = Mock(spec=[])  # type: Union[Mock, Type[Model]]


def test_resolve_string_template():
    template = resolve_template("blocks/header_block.html")
    assert template.template.name == "blocks/header_block.html"


def test_resolve_template_tuple():
    template = resolve_template(
        ("blocks/missing.html", "blocks/header_block.html")
    )
    assert template.template.name == "blocks/header_block.html"


def test_resolve_missing_template():
    with pytest.raises(TemplateDoesNotExist):
        resolve_template("blocks/missing.html")


def test_resolve_template_engine():
    template = resolve_template("blocks/header_block.html", using=None)
    assert template.backend.name == "jinja2"

    template = resolve_template("blocks/header_block.html", using="django")
    assert template.backend.name == "django"

    template = resolve_template("blocks/header_block.html", using="jinja2")
    assert template.backend.name == "jinja2"


def test_render_template_content():
    instance = HeaderBlock(text="Example header")
    assert render_template(instance) == "<h1>Example header</h1>"


def test_render_missing_template():
    with pytest.raises(TemplateDoesNotExist, match="blocks/listblock.html, blocks/list_block.html"):
        assert render_template(Mock(
            spec=["title", "_meta", "__class__"],
            __class__=Mock(
                __name__="ListBlock"
            ),
            _meta=Mock(
                app_label="blocks",
            ),
            title="Example title"
        ))


def test_render_missing_custom_template():
    with pytest.raises(TemplateDoesNotExist, match="blocks/missing.html"):
        assert render_template(Mock(
            spec=["StreamBlockMeta", "_meta"],
            _meta=Mock(
                app_label="blocks",
                model_name="headerblock",
            ),
            StreamBlockMeta=Mock(
                template="blocks/missing.html",
                engine=None
            ),
        ))
