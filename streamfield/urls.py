from django.contrib import admin
from django.urls import path

from .admin.views import RenderStreamView

app_name = "streamfields"
urlpatterns = [
    path("render-stream/", admin.site.admin_view(RenderStreamView.as_view()), name="render-stream"),
]
