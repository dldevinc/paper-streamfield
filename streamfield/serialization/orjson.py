import orjson as json  # noqa

__all__ = [
    "dumps", "loads"
]


def dumps(value) -> str:
    return json.dumps(value, option=json.OPT_SORT_KEYS | json.OPT_INDENT_2).decode()


def loads(value: str):
    return json.loads(value)
