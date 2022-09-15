from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import get_template, select_template

from . import conf
from .typing import BlockInstance
from .utils import camel_case_to_snake_case


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
        app_label, model_name = block._meta.app_label, block.__class__.__name__
        block_template = (
            "%s/%s.html" % (app_label, model_name.lower()),
            "%s/%s.html" % (app_label, camel_case_to_snake_case(model_name)),
        )

    template_engine = getattr(block, "block_template_engine", conf.DEFAULT_TEMPLATE_ENGINE)
    template = resolve_template(block_template, using=template_engine)

    context = {
        "block": block
    }
    context.update(extra_context or {})
    return template.render(context, request=request)
