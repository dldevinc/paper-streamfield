from typing import Any, Callable, Dict, Type

from django.db import models

BlockModel = Type[models.Model]
BlockInstance = models.Model
RenderFuncCallable = Callable[[BlockInstance, Dict[str, Any]], str]
