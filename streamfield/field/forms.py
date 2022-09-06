import json

from django.apps import apps
from django.db.models import Model
from django.forms import JSONField

from .widgets import StreamWidget


class StreamField(JSONField):
    widget = StreamWidget

    def __init__(self, **kwargs):
        self.models = kwargs.pop("models", [])
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["data-allowed-models"] = self.get_allowed_models()
        return attrs

    def get_allowed_models(self):
        allowed_models = []
        for model in self.models:
            if isinstance(model, str):
                model = apps.get_model(model)
            elif issubclass(model, Model):
                pass
            else:
                raise TypeError(model)

            opts = model._meta
            allowed_models.append(f"{opts.app_label}.{opts.model_name}")

        return json.dumps(allowed_models)
