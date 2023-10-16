import pytest
from blocks.models import *
from django.core.cache import cache
from django.template.exceptions import TemplateDoesNotExist

from streamfield.processors import DefaultProcessor

from .mock import get_mock


class TestInitialization:
    def test_custom_attributes(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
            theme="dark",
            key="sd94mGvS"
        )
        assert hasattr(processor, "theme")
        assert hasattr(processor, "key")

    def test_ignored_attributes(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
            processor="some value",
            _private_key="42"
        )
        assert not hasattr(processor, "processor")
        assert not hasattr(processor, "_private_key")

    def test_model(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock"
        )
        assert processor.model is HeaderBlock

    def test_invalid_model(self):
        with pytest.raises(LookupError):
            DefaultProcessor(
                app_label="unknown",
                model_name="HeaderBlock"
            )


class TestQueryset:
    def test_queryset(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock"
        )
        queryset = processor.get_queryset()
        assert queryset.model is HeaderBlock

    def test_select_related(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
            select_related="reviews"
        )
        queryset = processor.get_queryset()
        assert queryset.query.select_related == {
            "reviews": {}
        }

    def test_select_related_multiple(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
            select_related=["reviews", "authors"]
        )
        queryset = processor.get_queryset()
        assert queryset.query.select_related == {
            "reviews": {},
            "authors": {},
        }


class TestRendering:
    def test_default_template_names(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
        )

        block = get_mock()
        assert processor.get_template_names(block) == (
            "blocks/headerblock.html",
            "blocks/header_block.html",
        )

    def test_missing_templates(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
            template_name=["unknown/headerblock.html", "unknown/header_block.html"]
        )

        block = get_mock()
        with pytest.raises(TemplateDoesNotExist, match="unknown/headerblock.html, unknown/header_block.html"):
            processor.render(block)

    def test_default_context(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
        )

        block = get_mock()
        assert processor.get_context(block) == {
            "block": block
        }

    def test_rendering(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
        )

        block = get_mock(
            spec=["rank", "text"],
            rank="2",
            text="Hello world",
        )
        assert processor.render(block) == "<h2>Hello world</h2>"

    def test_parent_context(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
        )

        block = get_mock(
            spec=["rank", "text"],
            rank="2",
            text="Dark header",
        )
        assert processor.render(block, {
            "theme": "dark"
        }) == '<h2 class="header--dark">Dark header</h2>'


@pytest.mark.django_db
class TestCaching:
    def test_default_cache_key(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
        )

        block = get_mock(
            spec=["pk"],
            pk="26",
        )
        assert processor.get_cache_key(block) == "blocks.HeaderBlock:26"

    def test_default_cache_ttl(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
        )

        block = get_mock()
        assert processor.get_cache_ttl(block) == 3600

    def test_caching(self):
        processor = DefaultProcessor(
            app_label="blocks",
            model_name="HeaderBlock",
            cache=True
        )

        block = get_mock(
            spec=["pk", "rank", "text"],
            pk="26",
            rank="2",
            text="Hello world",
        )

        # clear cache
        cache_key = processor.get_cache_key(block)
        if cache_key in cache:
            cache.delete(cache_key)

        assert cache_key not in cache
        assert processor.render(block) == "<h2>Hello world</h2>"
        assert cache_key in cache

        same_block = get_mock(
            spec=["pk"],
            pk="26"
        )
        assert processor.render(same_block) == "<h2>Hello world</h2>"

        # clear cache
        cache_key = processor.get_cache_key(block)
        if cache_key in cache:
            cache.delete(cache_key)
