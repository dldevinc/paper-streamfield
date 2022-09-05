from django.contrib import admin

from streamfield.admin import StreamBlockAdmin

from .models import HeaderBlock, ImageBlock, TextBlock


@admin.register(HeaderBlock)
class HeaderBlockAdmin(StreamBlockAdmin):
    list_display = ["__str__", "rank"]


@admin.register(ImageBlock)
class ImageBlockAdmin(StreamBlockAdmin):
    list_display = ["__str__", "title"]


@admin.register(TextBlock)
class TextBlockAdmin(StreamBlockAdmin):
    pass
