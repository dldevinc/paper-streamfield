from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from streamfield.models import StreamField


class Page(models.Model):
    header = models.CharField(
        _("header"),
        max_length=128
    )
    slug = models.SlugField(
        _("slug"),
    )
    text = models.TextField(
        _("text"),
        blank=True
    )
    stream = StreamField(_("stream"))

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.header

    def get_absolute_url(self):
        return reverse("app:detail", kwargs={
            "slug": self.slug
        })
