import json
from typing import Dict

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.template.library import Library
from django.utils.safestring import mark_safe

from .. import blocks
from ..logging import logger

try:
    import jinja2
except ImportError:
    jinja2 = None


register = Library()


def _render_stream(stream: str, context: Dict, request: WSGIRequest) -> str:
    if isinstance(stream, str):
        stream = json.loads(stream)

    if not all(blocks.is_valid(record) for record in stream):
        logger.warning("Invalid stream value")
        return ""

    output = []
    for record in stream:
        try:
            block = blocks.from_dict(record)
        except (LookupError, ObjectDoesNotExist, MultipleObjectsReturned):
            logger.warning("Invalid block: %r", record)
            continue
        else:
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
def do_render_stream(context, stream: str):
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
        def _render_stream(stream: str, context):
            request = context.get("request", None)
            return _render_stream(stream, context, request=request)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(StreamFieldExtension)
