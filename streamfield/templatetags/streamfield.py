from django.template.library import Library
from django.utils.safestring import mark_safe
from jinja2_simple_tags import StandaloneTag

from .. import blocks, helpers

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


@register.simple_tag(name="render_block", takes_context=True)
def do_render_block(context, instance, **kwargs):
    ctx_dict = context.push(kwargs)
    processor = blocks.get_processor(type(instance))
    output = processor.render(instance, ctx_dict.context.flatten())
    return mark_safe(output)


if jinja2 is not None:
    class RenderStreamExtension(StandaloneTag):
        safe_output = True
        tags = {"render_stream"}

        def render(self, stream: str, **kwargs):
            context_vars = dict(self.context.get_all(), **kwargs)
            return helpers.render_stream(stream, context_vars)


    class RenderBlockExtension(StandaloneTag):
        safe_output = True
        tags = {"render_block"}

        def render(self, instance, **kwargs):
            context_vars = dict(self.context.get_all(), **kwargs)
            processor = blocks.get_processor(type(instance))
            return processor.render(instance, context_vars)


    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.extension(RenderStreamExtension)
        library.extension(RenderBlockExtension)
