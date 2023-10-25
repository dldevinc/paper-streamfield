import pytest
from blocks.models import HeaderBlock, TextBlock
from django.template.backends.django import DjangoTemplates
from jinja2 import Environment, FileSystemLoader

from streamfield import conf
from streamfield.templatetags.streamfield import (
    RenderBlockExtension,
    RenderStreamExtension,
)


@pytest.mark.django_db
class TestJinja2:
    def setup_method(self):
        self.env = Environment(
            loader=FileSystemLoader("tests/blocks/jinja2"),
            extensions=[RenderStreamExtension, RenderBlockExtension],
            autoescape=True
        )

    def test_parent_context(self):
        HeaderBlock.objects.create(
            pk=1,
            rank=3,
            text="Example header"
        )
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )
        template = self.env.from_string("<div>{% render_stream stream %}</div>")
        assert template.render({
            "theme": "new-year",
            "stream": '['
                      '{"uuid": "1234-5678", "model": "blocks.headerblock", "pk": "1"},'
                      '{"uuid": "1234-5679", "model": "blocks.textblock", "pk": "1"}'
                      ']'
        }) == ("<div>"
               "<h3 class=\"header--new-year\">Example header</h3>\n"
               "<div class=\"text--new-year\"><p>Example text</p></div>"
               "</div>")

    def test_render_block(self):
        header_block = HeaderBlock.objects.create(
            pk=1,
            rank=2,
            text="Happy New Year"
        )
        template = self.env.from_string("<div>{% render_block block %}</div>")
        assert template.render({
            "theme": "new-year",
            "block": header_block
        }) == ("<div>"
               "<h2 class=\"header--new-year\">Happy New Year</h2>"
               "</div>")


@pytest.mark.django_db
class TestDjango:
    def setup_method(self):
        self.env = DjangoTemplates({
            "NAME": "django",
            "DIRS": ["tests/blocks/templates"],
            "APP_DIRS": False,
            "OPTIONS": {
                "autoescape": True
            }
        })

    def test_parent_context(self):
        HeaderBlock.objects.create(
            pk=1,
            rank=3,
            text="Example header"
        )
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )

        assert conf.DEFAULT_TEMPLATE_ENGINE is None
        conf.DEFAULT_TEMPLATE_ENGINE = "django"

        template = self.env.from_string("{% load streamfield %}<div>{% render_stream stream %}</div>")
        assert template.render({
            "theme": "new-year",
            "stream": '['
                      '{"uuid": "1234-5678", "model": "blocks.headerblock", "pk": "1"},'
                      '{"uuid": "1234-5679", "model": "blocks.textblock", "pk": "1"}'
                      ']'
        }) == ("<div>"
               "<h3 class=\"header--new-year\">Example header</h3>\n"
               "<div class=\"text--new-year\"><p>Example text</p></div>"
               "</div>")

        conf.DEFAULT_TEMPLATE_ENGINE = None

    def test_render_block(self):
        header_block = HeaderBlock.objects.create(
            pk=1,
            rank=2,
            text="Happy New Year"
        )

        assert conf.DEFAULT_TEMPLATE_ENGINE is None
        conf.DEFAULT_TEMPLATE_ENGINE = "django"

        template = self.env.from_string("{% load streamfield %}<div>{% render_block block %}</div>")
        assert template.render({
            "theme": "new-year",
            "block": header_block
        }) == ("<div>"
               "<h2 class=\"header--new-year\">Happy New Year</h2>"
               "</div>")

        conf.DEFAULT_TEMPLATE_ENGINE = None
