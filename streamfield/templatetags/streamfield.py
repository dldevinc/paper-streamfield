from typing import Dict, Sequence

from django.core.handlers.wsgi import WSGIRequest
from django.template import Library
from django.utils.safestring import mark_safe

from .. import blocks

try:
    import jinja2
except ImportError:
    jinja2 = None


register = Library()


def _render_stream(stream: Sequence, context: Dict, request: WSGIRequest) -> str:
    output = []
    for record in stream:
        block = blocks.from_dict(record)
        if block is not None:
            output.append(
                blocks.render(
                    block,
                    extra_context={
                        "parent_context": context
                    },
                    request=request
                )
            )

    return "\n".join(output)


@register.simple_tag(name="render_stream", takes_context=True)
def do_render_stream(context, stream: Sequence):
    request = context.get("request", None)
    output = _render_stream(stream, context.flatten(), request=request)
    return mark_safe(output)


if jinja2 is not None:
    from jinja2 import nodes
    from jinja2.ext import Extension


    class StreamFieldExtension(Extension):
        tags = {"render_stream"}

        def parse(self, parser):
            lineno = next(parser.stream).lineno
            kwargs = [
                nodes.Keyword("context", nodes.ContextReference())
            ]

            args = []
            while parser.stream.current.type != 'block_end':
                args.append(parser.parse_expression())

            block_call = self.call_method("_render_stream", args, kwargs=kwargs)
            call = nodes.MarkSafe(block_call, lineno=lineno)
            return nodes.Output([call], lineno=lineno)

        @staticmethod
        def _render_stream(stream: Sequence, context):
            request = context.get("request", None)
            return _render_stream(stream, context, request=request)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(StreamFieldExtension)
