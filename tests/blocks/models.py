from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from streamfield.decorators import streamblock


@streamblock(icon="blocks/icons/header.svg")
class HeaderBlock(models.Model):
    header = models.CharField(
        _("header"),
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

    def __str__(self):
        return self.header


@streamblock(icon="blocks/icons/image.svg")
class TextBlock(models.Model):
    text = models.TextField(
        _("text")
    )

    class Meta:
        verbose_name = "Text"
        verbose_name_plural = "Text"

    def __str__(self):
        return Truncator(self.text).chars(64)


@streamblock(icon="blocks/icons/text.svg")
class ImageBlock(models.Model):
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
