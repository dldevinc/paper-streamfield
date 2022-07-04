from json import JSONDecodeError

from django.core import checks
from django.core.exceptions import ValidationError
from django.db import connections, models, router
from django.db.models import NOT_PROVIDED
from django.db.models.fields.json import KeyTransform, KeyTransformFactory
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.utils.translation import gettext_lazy as _

from ..serialization import dumps, loads
from . import forms


class StreamField(CheckFieldDefaultMixin, models.Field):
    empty_strings_allowed = False
    description = _("A JSON object")
    default_error_messages = {
        "invalid": _("Value must be valid JSON."),
    }
    _default_hint = ("list", "[]")

    def __init__(self, *args, **kwargs):
        default = kwargs.get("default")
        if default is NOT_PROVIDED or default is None:
            kwargs["default"] = list
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        databases = kwargs.get("databases") or []
        errors.extend(self._check_supported(databases))
        return errors

    def _check_supported(self, databases):
        errors = []
        for db in databases:
            if not router.allow_migrate_model(db, self.model):
                continue
            connection = connections[db]
            if (
                self.model._meta.required_db_vendor
                and self.model._meta.required_db_vendor != connection.vendor
            ):
                continue
            if not (
                "supports_json_field" in self.model._meta.required_db_features
                or connection.features.supports_json_field
            ):
                errors.append(
                    checks.Error(
                        "%s does not support JSONFields." % connection.display_name,
                        obj=self.model,
                        id="fields.E180",
                    )
                )
        return errors

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.default is None:
            del kwargs["default"]
        if self.blank is True:
            del kwargs["blank"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Some backends (SQLite at least) extract non-string values in their
        # SQL datatypes.
        if isinstance(expression, KeyTransform) and not isinstance(value, str):
            return value
        try:
            return loads(value)
        except JSONDecodeError:
            return value

    def get_internal_type(self):
        return "JSONField"

    def get_prep_value(self, value):
        if value is None:
            return value
        return dumps(value)

    def get_transform(self, name):
        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        try:
            dumps(value)
        except TypeError:
            raise ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )

    def value_to_string(self, obj):
        return self.value_from_object(obj)

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": forms.StreamField,
                **kwargs,
            }
        )
