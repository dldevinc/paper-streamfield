from django.db import models


class StreamBlockModelMixin:
    pass


class StreamBlockModel(StreamBlockModelMixin, models.Model):
    class Meta:
        abstract = True
