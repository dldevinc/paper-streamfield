from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from streamfield.field.models import StreamField


class Page(models.Model):
    header = models.CharField(
        _("header"),
        max_length=128
    )
    epigraph = models.ForeignKey(
        "blocks.TextBlock",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        _("slug"),
    )
    stream = StreamField(
        _("stream"),
        models=[
            "blocks.HeaderBlock",
            "blocks.ImageBlock",
            "blocks.TextBlock",
        ]
    )

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.header

    def get_absolute_url(self):
        return reverse("app:detail", kwargs={
            "slug": self.slug
        })


class Advantage(models.Model):
    title = models.TextField(
        _("title")
    )
    description = models.TextField(
        _("description")
    )

    class Meta:
        verbose_name = "advantage"

    def __str__(self):
        return self.title
