from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from streamfield.models import StreamBlockModel


class HeaderBlock(StreamBlockModel):
    header = models.CharField(
        _("header"),
        max_length=255
    )
    level = models.PositiveSmallIntegerField(
        _("level"),
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6)
        ]
    )

    class Meta:
        verbose_name = "Header"
        verbose_name_plural = "Headers"

    def __str__(self):
        return self.header


class TextBlock(StreamBlockModel):
    text = models.TextField(
        _("text")
    )

    class Meta:
        verbose_name = "Text"
        verbose_name_plural = "Text"

    def __str__(self):
        return Truncator(self.text).chars(64)


class ImageBlock(StreamBlockModel):
    image = models.ImageField(
        _("image")
    )
    title = models.CharField(
        _("title"),
        max_length=255,
        blank=True
    )
    alt = models.CharField(
        _("alt"),
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return self.title or "Image #{}".format(self.pk)
