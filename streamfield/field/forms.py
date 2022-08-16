from django.forms import JSONField

from .widgets import StreamWidget


class StreamField(JSONField):
    widget = StreamWidget
