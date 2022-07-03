from django.views import generic

from .models import Page


class IndexView(generic.TemplateView):
    template_name = "app/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pages"] = Page.objects.order_by("id")
        return context


class DetailView(generic.DetailView):
    model = Page
    context_object_name = "page"
    template_name = "app/detail.html"
