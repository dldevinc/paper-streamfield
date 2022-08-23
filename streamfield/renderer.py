from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.template.loader import get_template, select_template

from .models import Options
from .typing import BlockInstance, BlockModel


class TemplateRenderer:
    def __init__(self, model: BlockModel):
        self.meta = getattr(model, "_stream_meta", None)
        if self.meta is None:
            self.meta = Options()

    def __call__(self, block: BlockInstance, extra_context: Dict = None):
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
        context.setdefault("block", block)
        request = context.pop("request", None)
        return template.render(context, request)

    def resolve_template(self, name, using=None):
        if isinstance(name, (list, tuple)):
            return select_template(name, using=using)
        elif isinstance(name, str):
            return get_template(name, using=using)
        else:
            return name
