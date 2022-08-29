from django.urls import path

from .admin.views import render_streamblocks

app_name = "streamfields"
urlpatterns = [
    path("render/", render_streamblocks, name="render"),
]
