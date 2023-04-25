from django.contrib import admin
from django.urls import path

from .admin.views import RenderStreamView, RenderButtonsView

app_name = "streamfields"
urlpatterns = [
    path("render-stream/", admin.site.admin_view(RenderStreamView.as_view(admin_site=admin.site)), name="render-stream"),
    path("render-buttons/", admin.site.admin_view(RenderButtonsView.as_view(admin_site=admin.site)), name="render-buttons"),
]
