from django.contrib import admin
from django.urls import path

from .admin.views import RenderStreamView, RenderToolbarView

app_name = "streamfields"
urlpatterns = [
    path("render-stream/", admin.site.admin_view(RenderStreamView.as_view()), name="render-stream"),
    path("render-toolbar/", admin.site.admin_view(RenderToolbarView.as_view()), name="render-toolbar"),
]
