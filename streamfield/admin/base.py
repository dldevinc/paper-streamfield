from django.contrib import admin


class StreamBlockAdmin(admin.ModelAdmin):
    popup_response_template = "streamfield/popup_response.html"
