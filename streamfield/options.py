from typing import Callable, List, Tuple, Union

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from . import conf
from .typing import BlockInstance, BlockModel
from .utils import camel_case_to_snake_case


class StreamBlockOptions:
    def __init__(self, meta, app_label=None, model_name=None):
        self.app_label = app_label
        self.model_name = model_name
        self.meta = meta
        self._engine = getattr(meta, "engine", conf.DEFAULT_TEMPLATE_ENGINE)
        self._template_name = getattr(meta, "template", None)
        self._renderer = getattr(meta, "renderer", conf.DEFAULT_RENDERER)

    def __getattr__(self, item):
        return getattr(self.meta, item)

    @property
    def engine(self):
        return self._engine

    @property
    def template(self) -> Union[str, List[str], Tuple]:
        if self._template_name is not None:
            return self._template_name

        return (
            "%s/%s.html" % (self.app_label, self.model_name.lower()),
            "%s/%s.html" % (self.app_label, camel_case_to_snake_case(self.model_name)),
        )

    @property
    def renderer(self) -> Callable[..., str]:
        renderer = self._renderer
        if isinstance(renderer, str):
            renderer = import_string(renderer)

        if isinstance(renderer, type):
            renderer = renderer()

        if not callable(renderer):
            raise ImproperlyConfigured("%r object is not a callable" % renderer)

        return renderer


def get_block_opts(block: Union[BlockInstance, BlockModel]) -> StreamBlockOptions:
    meta = getattr(block, "StreamBlockMeta", None)
    app_label = block._meta.app_label
    model_name = block.__name__ if isinstance(block, type) else block.__class__.__name__
    return StreamBlockOptions(meta, app_label, model_name)
