from typing import Dict

from django.template import Library
from django.utils.safestring import mark_safe

from ..helpers import get_stream_blocks, render_block

try:
    import jinja2
except ImportError:
    jinja2 = None


register = Library()


@register.simple_tag(name="render_stream", takes_context=True)
def do_render_stream(context, stream: Dict):
    request = context.get("request", None)
    rendered_blocks = (
        render_block(block, {
            "parent_context": context.flatten()
        }, request=request)
        for block in get_stream_blocks(stream)
    )
    return mark_safe("\n".join(rendered_blocks))


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
        def _render_stream(stream: Dict, context):
            request = context.get("request", None)
            rendered_blocks = (
                render_block(block, {
                    "parent_context": context
                }, request=request)
                for block in get_stream_blocks(stream)
            )
            return "\n".join(rendered_blocks)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(StreamFieldExtension)
