from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import get_template, select_template

from .models import Options
from .typing import BlockInstance, BlockModel


class BaseRenderer:
    def __init__(self, model: BlockModel):
        self.meta = getattr(model, "_stream_meta", Options())

    def __call__(self, block: BlockInstance, extra_context: Dict = None, request: WSGIRequest = None):
        raise NotImplementedError


class TemplateRenderer(BaseRenderer):
    context_object_name = "block"

    def __call__(self, block: BlockInstance, extra_context: Dict = None, request: WSGIRequest = None) -> str:
        template_name = getattr(self.meta, "template", None)
        if template_name is None:
            raise ImproperlyConfigured(
                "Model class %s.%s requires either a definition of 'template_name'"
                % (block._meta.app_label, block._meta.model_name)
            )

        template_engine = getattr(self.meta, "template_engine", None)
        template = self.resolve_template(template_name, using=template_engine)

        context = getattr(self.meta, "context", None) or {}
        context.update(extra_context or {})
        context.setdefault(self.context_object_name, block)
        return template.render(context, request=request)

    def resolve_template(self, name, using=None):
        if isinstance(name, (list, tuple)):
            return select_template(name, using=using)
        elif isinstance(name, str):
            return get_template(name, using=using)
        else:
            return name
