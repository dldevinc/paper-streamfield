from django.template.library import Library
from django.utils.safestring import mark_safe

from .. import helpers

try:
    import jinja2
except ImportError:
    jinja2 = None


register = Library()


@register.simple_tag(name="render_stream", takes_context=True)
def do_render_stream(context, stream: str):
    request = context.get("request", None)
    output = helpers.render_stream(stream, context.flatten(), request=request)
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
            return helpers.render_stream(stream, context, request=request)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(StreamFieldExtension)
