try:
    import orjson as _orjson
except ImportError:
    from .json import dumps, loads  # noqa: F403
else:
    from .orjson import dumps, loads  # noqa: F403

__all__ = ["dumps", "loads"]
