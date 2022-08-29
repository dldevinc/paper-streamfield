from django.forms.widgets import Textarea


class StreamWidget(Textarea):
    template_name = "streamfield/widget.html"

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.setdefault("class", "stream-field__textarea")
        super().__init__(attrs)

    class Media:
        css = {
            "all": [
                "streamfield/widget.css",
            ]
        }
        js = [
            "streamfield/widget.js",
        ]
