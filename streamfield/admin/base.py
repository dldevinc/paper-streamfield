from django.contrib import admin


class StreamBlockModelAdminMixin:
    stream_block_template = "streamfield/admin/block.html"


class StreamBlockModelAdmin(StreamBlockModelAdminMixin, admin.ModelAdmin):
    """
    Базовый класс интерфейса администратора для блоков.
    """
    pass
