from django.contrib import admin

from .models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ["header", "slug"]
        }),
        (None, {
            "fields": ["stream"]
        }),
    )
    ordering = ["id"]
    prepopulated_fields = {
        "slug": ["header"]
    }
