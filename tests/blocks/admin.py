from django.contrib import admin

from streamfield.admin import StreamBlockModelAdmin

from .models import HeaderBlock, ImageBlock, TextBlock, QuoteBlock, AdvantagesBlock


@admin.register(HeaderBlock)
class HeaderBlockAdmin(StreamBlockModelAdmin):
    list_display = ["__str__", "rank"]


@admin.register(ImageBlock)
class ImageBlockAdmin(StreamBlockModelAdmin):
    stream_block_template = "blocks/admin/image.html"
    list_display = ["__str__", "title"]


@admin.register(TextBlock)
class TextBlockAdmin(StreamBlockModelAdmin):
    pass


@admin.register(QuoteBlock)
class QuoteBlockAdmin(StreamBlockModelAdmin):
    pass


@admin.register(AdvantagesBlock)
class AdvantagesBlockAdmin(StreamBlockModelAdmin):
    pass
