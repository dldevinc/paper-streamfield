from django.contrib import admin
from django.urls import path

from .admin.views import RenderFieldView

app_name = "streamfields"
urlpatterns = [
    path("render/", admin.site.admin_view(RenderFieldView.as_view()), name="render"),
]
