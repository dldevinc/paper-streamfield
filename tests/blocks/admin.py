from django.contrib import admin

from streamfield.admin import StreamBlockModelAdmin

from .models import HeaderBlock, ImageBlock, TextBlock


@admin.register(HeaderBlock)
class HeaderBlockAdmin(StreamBlockModelAdmin):
    list_display = ["__str__", "rank"]


@admin.register(ImageBlock)
class ImageBlockAdmin(StreamBlockModelAdmin):
    list_display = ["__str__", "title"]


@admin.register(TextBlock)
class TextBlockAdmin(StreamBlockModelAdmin):
    pass
