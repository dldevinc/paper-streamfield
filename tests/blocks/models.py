from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from streamfield.models import StreamBlockModel


class HeaderBlock(StreamBlockModel):
    text = models.CharField(
        _("text"),
        max_length=255
    )
    rank = models.PositiveSmallIntegerField(
        _("rank"),
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6)
        ],
        help_text="The most important heading has the rank 1 (&lt;h1&gt;), the least important heading rank 6 (&lt;h6&gt;). "
                  "Headings with an equal or higher rank start a new section, headings with a lower rank start new "
                  "subsections that are part of the higher ranked section."
    )

    class Meta:
        verbose_name = "Header"
        verbose_name_plural = "Headers"

    class StreamBlockMeta:
        template = "blocks/header.html"

    def __str__(self):
        return self.text


class TextBlock(StreamBlockModel):
    text = models.TextField(
        _("text")
    )

    class Meta:
        verbose_name = "Text"
        verbose_name_plural = "Text"

    class StreamBlockMeta:
        template = "blocks/text.html"

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

    class StreamBlockMeta:
        template = "blocks/image.html"

    def __str__(self):
        return self.title or "Image #{}".format(self.pk)
