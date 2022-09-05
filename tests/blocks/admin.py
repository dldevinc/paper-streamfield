from streamfield import admin

from .models import HeaderBlock, ImageBlock, TextBlock


@admin.register(HeaderBlock)
class HeaderBlockAdmin(admin.ModelAdmin):
    list_display = ["__str__", "rank"]


@admin.register(ImageBlock)
class ImageBlockAdmin(admin.ModelAdmin):
    list_display = ["__str__", "title"]


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    pass
