from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from .processors import AdvantagesBlockProcessor

__all__ = ["HeaderBlock", "TextBlock", "ImageBlock", "QuoteBlock", "AdvantagesBlock"]


class HeaderBlock(models.Model):
    text = models.TextField(
        _("text")
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

    def __str__(self):
        return self.text


class TextBlock(models.Model):
    text = models.TextField(
        _("text")
    )

    class Meta:
        verbose_name = "Text"

    class StreamBlockMeta:
        template_name = "blocks/text.html"

    def __str__(self):
        return Truncator(self.text).chars(96)


class ImageBlock(models.Model):
    image = models.URLField(
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

    def __str__(self):
        return self.title or "Image #{}".format(self.pk)


class QuoteBlock(models.Model):
    text = models.TextField(
        _("text")
    )
    author = models.CharField(
        _("author"),
        max_length=128
    )

    class Meta:
        verbose_name = "Quote"

    def __str__(self):
        return Truncator(
            "{}: {}".format(self.author, self.text)
        ).chars(96)


class AdvantagesBlock(models.Model):
    header = models.TextField(
        _("header")
    )

    class Meta:
        verbose_name = "Advantages"

    class StreamBlockMeta:
        template_name = "blocks/advantages.html"
        processor = AdvantagesBlockProcessor

    def __str__(self):
        return "Advantages Block"
