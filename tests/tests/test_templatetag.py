import pytest
from jinja2 import Environment, FileSystemLoader

from blocks.models import TextBlock

from django.template.backends.django import DjangoTemplates
from streamfield.templatetags.streamfield import StreamFieldExtension


@pytest.mark.django_db
class TestJinja2:
    def setup_method(self):
        self.env = Environment(
            loader=FileSystemLoader("tests/blocks/jinja2"),
            extensions=[StreamFieldExtension],
            autoescape=True
        )

    def test_parent_context(self):
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )
        template = self.env.from_string("<div>{% render_stream stream %}</div>")
        assert template.render({
            "theme": "new-year",
            "stream": '[{"uuid": "1234-5678", "model": "blocks.textblock", "pk": "1"}]'
        }) == "<div><div class=\"text--new-year\"><p>Example text</p></div></div>"


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
        TextBlock.objects.create(
            pk=1,
            text="Example text"
        )
        template = self.env.from_string("{% load streamfield %}<div>{% render_stream stream %}</div>")
        assert template.render({
            "theme": "new-year",
            "stream": '[{"uuid": "1234-5678", "model": "blocks.textblock", "pk": "1"}]'
        }) == "<div><div class=\"text--new-year\"><p>Example text</p></div></div>"
