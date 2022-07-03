from django.urls import path

from .views import DetailView, IndexView

app_name = "app"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("<slug:slug>/", DetailView.as_view(), name="detail"),
]
