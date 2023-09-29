import pytest

from streamfield import conf
from streamfield.options import get_block_opts
from streamfield.renderers import CacheRenderer, DefaultRenderer

from .mock import get_mock


@pytest.mark.django_db
class TestOptions:
    def test_app_label(self):
        opts = get_block_opts(get_mock(
            spec=["_meta"],
            _meta=get_mock(
                app_label="app",
            )
        ))
        assert opts.app_label == "app"

    def test_model_name(self):
        opts = get_block_opts(get_mock(
            spec=["__class__", "_meta"],
            __class__=get_mock(
                __name__="HeaderBlock"
            ),
        ))
        assert opts.model_name == "HeaderBlock"

    def test_default_engine(self):
        assert conf.DEFAULT_TEMPLATE_ENGINE is None
        conf.DEFAULT_TEMPLATE_ENGINE = "jinja2"
        opts = get_block_opts(get_mock(
            spec=["_meta"]
        ))
        assert opts.engine == "jinja2"
        conf.DEFAULT_TEMPLATE_ENGINE = None

    def test_custom_engine(self):
        opts = get_block_opts(get_mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=get_mock(
                engine="jinja2"
            )
        ))
        assert opts.engine == "jinja2"

    def test_default_renderer(self):
        assert conf.DEFAULT_RENDERER == "streamfield.renderers.DefaultRenderer"
        opts = get_block_opts(get_mock(
            spec=["_meta"]
        ))
        assert isinstance(opts.renderer, DefaultRenderer)

    def test_custom_renderer(self):
        assert conf.DEFAULT_RENDERER == "streamfield.renderers.DefaultRenderer"
        opts = get_block_opts(get_mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=get_mock(
                renderer="streamfield.renderers.CacheRenderer"
            )
        ))
        assert isinstance(opts.renderer, CacheRenderer)

    def test_default_template(self):
        opts = get_block_opts(get_mock(
            spec=["__class__", "_meta"],
            __class__=get_mock(
                __name__="HeaderBlock"
            ),
            _meta=get_mock(
                app_label="app"
            ),
        ))
        assert opts.template == (
            "app/headerblock.html",
            "app/header_block.html",
        )

    def test_custom_template(self):
        opts = get_block_opts(get_mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=get_mock(
                template="blocks/header.html"
            )
        ))
        assert opts.template == "blocks/header.html"

    def test_custom_options(self):
        opts = get_block_opts(get_mock(
            spec=["_meta", "StreamBlockMeta"],
            StreamBlockMeta=get_mock(
                password="secret"
            )
        ))
        assert opts.password == "secret"
