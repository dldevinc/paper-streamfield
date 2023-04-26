from django.contrib import admin


class StreamBlockModelAdminMixin:
    popup_response_template = "streamfield/admin/popup_response.html"
    stream_block_template = "streamfield/admin/block.html"


class StreamBlockModelAdmin(StreamBlockModelAdminMixin, admin.ModelAdmin):
    """
    Базовый класс интерфейса администратора для блоков.
    """
    pass
