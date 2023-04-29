from unittest.mock import Mock

import pytest

from streamfield import conf
from streamfield.options import get_block_opts
from streamfield.renderer import CacheRenderer, DefaultRenderer


@pytest.mark.django_db
class TestOptions:
    def test_app_label(self):
        opts = get_block_opts(Mock(
            spec=["_meta"],
            _meta=Mock(
                app_label="app",
            )
        ))
        assert opts.app_label == "app"

    def test_model_name(self):
        opts = get_block_opts(Mock(
            spec=["__class__", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
        ))
        assert opts.model_name == "HeaderBlock"

    def test_default_engine(self):
        assert conf.DEFAULT_TEMPLATE_ENGINE is None
        conf.DEFAULT_TEMPLATE_ENGINE = "jinja2"
        opts = get_block_opts(Mock(
            spec=["_meta"]
        ))
        assert opts.engine == "jinja2"
        conf.DEFAULT_TEMPLATE_ENGINE = None

    def test_custom_engine(self):
        opts = get_block_opts(Mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=Mock(
                engine="jinja2"
            )
        ))
        assert opts.engine == "jinja2"

    def test_default_renderer(self):
        assert conf.DEFAULT_RENDERER == "streamfield.renderer.DefaultRenderer"
        opts = get_block_opts(Mock(
            spec=["_meta"]
        ))
        assert isinstance(opts.renderer, DefaultRenderer)

    def test_custom_renderer(self):
        assert conf.DEFAULT_RENDERER == "streamfield.renderer.DefaultRenderer"
        opts = get_block_opts(Mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=Mock(
                renderer="streamfield.renderer.CacheRenderer"
            )
        ))
        assert isinstance(opts.renderer, CacheRenderer)

    def test_default_template(self):
        opts = get_block_opts(Mock(
            spec=["__class__", "_meta"],
            __class__=Mock(
                __name__="HeaderBlock"
            ),
            _meta=Mock(
                app_label="app"
            ),
        ))
        assert opts.template == (
            "app/headerblock.html",
            "app/header_block.html",
        )

    def test_custom_template(self):
        opts = get_block_opts(Mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=Mock(
                template="blocks/header.html"
            )
        ))
        assert opts.template == "blocks/header.html"

    def test_custom_options(self):
        opts = get_block_opts(Mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=Mock(
                password="secret"
            )
        ))
        assert opts.password == "secret"
