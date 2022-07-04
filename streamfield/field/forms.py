from json import JSONDecodeError

from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import InvalidJSONInput
from django.utils.translation import gettext_lazy as _

from .serialization import dumps, loads
from .widgets import StreamWidget


class StreamField(forms.CharField):
    default_error_messages = {
        "invalid": _("Enter a valid JSON."),
    }
    widget = StreamWidget

    def to_python(self, value):
        if self.disabled:
            return value

        if value in self.empty_values:
            return None
        elif isinstance(value, (list, dict, int, float)):
            return value

        try:
            return loads(value)
        except JSONDecodeError:
            raise ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )

    def bound_data(self, data, initial):
        if self.disabled:
            return initial

        if data is None:
            return None

        try:
            return loads(data)
        except JSONDecodeError:
            return InvalidJSONInput(data)

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return dumps(value)

    def has_changed(self, initial, data):
        if super().has_changed(initial, data):
            return True

        # For purposes of seeing whether something has changed, True isn't the
        # same as 1 and the order of keys doesn't matter.
        return dumps(initial) != dumps(self.to_python(data))
