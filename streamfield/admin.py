from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage


class StreamBlockModelAdmin(admin.ModelAdmin):
    streamfield_icon = "streamfield/default.svg"

    def get_streamfield_icon(self):
        return staticfiles_storage.url(self.streamfield_icon)
