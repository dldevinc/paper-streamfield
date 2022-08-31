from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.db.models.base import ModelBase

from streamfield import conf


class Options:
    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __eq__(self, other):
        if not isinstance(other, Options):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__


class StreamBlockMetaClass(ModelBase):
    """Metaclass for all StreamBlock models."""

    def __new__(cls, name, bases, attrs, **kwargs):
        meta_class = attrs.pop("StreamBlockMeta", None)
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        if not new_class._meta.abstract and meta_class is None:
            raise ImproperlyConfigured(
                "Model class %s doesn't declare an explicit internal class StreamBlockMeta." % name
            )

        meta_attrs = {
            name: value
            for name, value in meta_class.__dict__.items()
            if not name.startswith("_")
        } if meta_class else {}

        meta_attrs.setdefault("renderer", conf.DEFAULT_RENDERER)

        new_class._stream_meta = Options(**meta_attrs)
        return new_class


class StreamBlockModel(Model, metaclass=StreamBlockMetaClass):
    class Meta:
        abstract = True
