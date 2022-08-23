from typing import Any, Callable, Dict, Type, Union

from django.db.models import Model

BlockModel = Type[Model]
BlockInstance = Model
RenderFuncCallable = Callable[[BlockInstance, Dict[str, Any]], str]
RenderFunc = Union[str, RenderFuncCallable]
