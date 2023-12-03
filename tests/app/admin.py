from django.contrib import admin

from .models import Page, Advantage


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ["header", "slug"]
        }),
        (None, {
            "fields": ["epigraph", "stream"]
        }),
    )
    ordering = ["id"]
    prepopulated_fields = {
        "slug": ["header"]
    }


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                "title", "description"
            ),
        }),
    )
