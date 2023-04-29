from django.template.library import Library
from django.utils.safestring import mark_safe
from jinja2_simple_tags import StandaloneTag

from .. import helpers

try:
    import jinja2
except ImportError:
    jinja2 = None

register = Library()


@register.simple_tag(name="render_stream", takes_context=True)
def do_render_stream(context, stream: str, **kwargs):
    request = context.get("request", None)
    context = dict(kwargs, **{
        "parent_context": context.flatten(),
    })
    output = helpers.render_stream(stream, context, request=request)
    return mark_safe(output)


if jinja2 is not None:
    class StreamFieldExtension(StandaloneTag):
        safe_output = True
        tags = {"render_stream"}

        def render(self, stream: str, **kwargs):
            request = self.context.get("request", None)
            context = dict(kwargs, **{
                "parent_context": self.context,
            })
            return helpers.render_stream(stream, context, request=request)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(StreamFieldExtension)
