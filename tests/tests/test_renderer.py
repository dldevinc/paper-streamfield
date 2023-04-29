from datetime import datetime
from typing import Type, Union
from unittest.mock import Mock

import pytest
from django.core.cache import cache
from django.db.models import Model
from django.template import TemplateDoesNotExist

from streamfield.renderer import CacheRenderer, DefaultRenderer

DummyModel = Mock(spec=[])  # type: Union[Mock, Type[Model]]


class TestDefaultRenderer:
    def test_missing_template(self):
        renderer = DefaultRenderer()
        with pytest.raises(TemplateDoesNotExist, match="app/headerblock.html, app/header_block.html"):
            renderer(Mock(
                spec=["__class__", "_meta"],
                __class__=Mock(
                    __name__="HeaderBlock"
                ),
                _meta=Mock(
                    app_label="app",
                )
            ))

    def test_context(self):
        renderer = DefaultRenderer()
        block = Mock(
            spec=["__class__", "rank", "text", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            rank="2",
            text="Hello world",
            _meta=Mock(
                app_label="blocks",
            )
        )
        assert renderer.get_context(block, classes="heading--level-1") == {
            "block": block,
            "classes": "heading--level-1"
        }

    def test_content(self):
        renderer = DefaultRenderer()
        assert renderer(Mock(
            spec=["__class__", "rank", "text", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            rank="2",
            text="Hello world",
            _meta=Mock(
                app_label="blocks",
            )
        )) == "<h2>Hello world</h2>"


class TestCacheRenderer:
    def test_default_cache(self):
        renderer = CacheRenderer()
        assert renderer.get_cache(Mock(
            spec=["_meta"]
        )).key_prefix == "default"

    def test_custom_cache(self):
        renderer = CacheRenderer()
        assert renderer.get_cache(Mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=Mock(
                cache_backend="secondary"
            )
        )).key_prefix == "secondary"

    def test_cache_key(self):
        renderer = CacheRenderer()
        block = Mock(
            spec=["__class__", "pk", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            pk="54",
            _meta=Mock(
                app_label="blocks",
            )
        )
        assert renderer.get_cache_key(block, classes="heading--level-1") == "blocks.HeaderBlock:54"

    def test_default_cache_ttl(self):
        renderer = CacheRenderer()
        assert renderer.get_cache_ttl(Mock(
            spec=["_meta"]
        )) is None

    def test_custom_cache_ttl(self):
        renderer = CacheRenderer()
        assert renderer.get_cache_ttl(Mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=Mock(
                cache_ttl=1800
            )
        )) == 1800

    def test_content(self):
        renderer = CacheRenderer()
        assert renderer(Mock(
            spec=["__class__", "pk", "rank", "text", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            pk=42,
            rank="2",
            text="Hello world",
            _meta=Mock(
                app_label="blocks",
            )
        )) == "<h2>Hello world</h2>"

    def test_actually_cached(self):
        renderer = CacheRenderer()
        assert renderer(Mock(
            spec=["__class__", "pk", "rank", "text", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            pk=69,
            rank="3",
            text="Hello world",
            _meta=Mock(
                app_label="blocks",
            )
        )) == "<h3>Hello world</h3>"

        assert renderer(Mock(
            spec=["__class__", "pk", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            pk=69,
            _meta=Mock(
                app_label="blocks",
            )
        )) == "<h3>Hello world</h3>"

    def test_default_cache_timeout(self):
        renderer = CacheRenderer()
        block = Mock(
            spec=["__class__", "pk", "rank", "text", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            pk=75,
            rank="4",
            text="Morning light",
            _meta=Mock(
                app_label="blocks",
            )
        )

        assert renderer(block) == "<h4>Morning light</h4>"

        # default cache timeout is 3600
        cache_key = cache.make_key(renderer.get_cache_key(block))
        ttl = datetime.fromtimestamp(cache._expire_info[cache_key]) - datetime.now()
        assert 3595 <= ttl.seconds < 3600
