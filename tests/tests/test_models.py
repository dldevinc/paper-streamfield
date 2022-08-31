from blocks.models import HeaderBlock
from streamfield.models import Options


def test_stream_meta_class():
    stream_meta = HeaderBlock._stream_meta
    assert isinstance(stream_meta, Options)


def test_stream_meta_fields():
    stream_meta = HeaderBlock._stream_meta
    assert stream_meta.template == "blocks/header.html"
    assert stream_meta.renderer == "streamfield.renderer.TemplateRenderer"
