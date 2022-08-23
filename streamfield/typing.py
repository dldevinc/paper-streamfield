from typing import Any, Callable, Dict

from .models import StreamBlockMetaClass, StreamBlockModel

BlockModel = StreamBlockMetaClass
BlockInstance = StreamBlockModel
RenderFuncCallable = Callable[[BlockInstance, Dict[str, Any]], str]
