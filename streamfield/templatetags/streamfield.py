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
    ctx_dict = context.push(kwargs)
    output = helpers.render_stream(stream, ctx_dict.context.flatten())
    return mark_safe(output)


if jinja2 is not None:
    class StreamFieldExtension(StandaloneTag):
        safe_output = True
        tags = {"render_stream"}

        def render(self, stream: str, **kwargs):
            context_vars = self.context.get_all()
            context_vars.update(kwargs)
            return helpers.render_stream(stream, context_vars)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(StreamFieldExtension)
