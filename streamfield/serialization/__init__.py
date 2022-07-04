try:
    import orjson as _orjson
except ImportError:
    from .json import *
else:
    from .orjson import *

__all__ = ["dumps", "loads"]
