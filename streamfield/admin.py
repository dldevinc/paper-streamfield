from django.contrib import admin

from .helpers import get_streamblocks_models


class StreamBlockModelAdmin(admin.ModelAdmin):
    pass


for model in get_streamblocks_models():
    if not admin.site.is_registered(model):
        admin.site.register(model, StreamBlockModelAdmin)
