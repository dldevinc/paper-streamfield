from django.forms.widgets import Textarea


class StreamWidget(Textarea):
    template_name = "streamfield/widget.html"

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.setdefault("class", "stream-field__control")
        super().__init__(attrs)

    class Media:
        css = {
            "all": [
                "streamfield/dist/widget.css",
            ]
        }
        js = [
            "streamfield/dist/widget.js",
        ]
