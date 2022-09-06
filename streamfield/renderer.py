from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import get_template, select_template

from .typing import BlockInstance


def resolve_template(name, using=None):
    if isinstance(name, (list, tuple)):
        return select_template(name, using=using)
    elif isinstance(name, str):
        return get_template(name, using=using)
    else:
        return name


def render_template(block: BlockInstance, extra_context: Dict = None, request: WSGIRequest = None) -> str:
    block_template = getattr(block, "block_template", None)
    if block_template is None:
        raise ImproperlyConfigured(
            "Model class '%s.%s' requires attribute 'block_template'."
            % (block._meta.app_label, block._meta.model_name)
        )

    template_engine = getattr(block, "block_template_engine", None)
    template = resolve_template(block_template, using=template_engine)

    context = {
        "block": block
    }
    context.update(extra_context or {})
    return template.render(context, request=request)
