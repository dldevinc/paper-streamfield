from django.db.models import NOT_PROVIDED, JSONField

from . import forms


class StreamField(JSONField):
    _default_hint = ("list", "[]")

    def __init__(self, *args, **kwargs):
        self.models = kwargs.pop("models", [])
        default = kwargs.get("default")
        if default is NOT_PROVIDED or default is None:
            kwargs["default"] = list
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.default is None:
            del kwargs["default"]
        if self.blank is True:
            del kwargs["blank"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": forms.StreamField,
                "models": self.models,
                **kwargs,
            }
        )
