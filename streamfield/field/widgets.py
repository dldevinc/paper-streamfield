from django.forms.widgets import Textarea


class StreamWidget(Textarea):
    template_name = "streamfield/widget.html"
