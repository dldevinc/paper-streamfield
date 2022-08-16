from django.contrib import admin

from streamfield.admin import StreamBlockModelAdmin

from .models import HeaderBlock, ImageBlock, TextBlock


@admin.register(HeaderBlock)
class HeaderBlockAdmin(StreamBlockModelAdmin):
    streamfield_icon = "blocks/icons/header.svg"


@admin.register(ImageBlock)
class ImageBlockAdmin(StreamBlockModelAdmin):
    streamfield_icon = "blocks/icons/image.svg"


@admin.register(TextBlock)
class TextBlockAdmin(StreamBlockModelAdmin):
    streamfield_icon = "blocks/icons/text.svg"
