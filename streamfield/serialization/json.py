import json

from django.core.serializers.json import DjangoJSONEncoder

__all__ = [
    "dumps", "loads"
]


def dumps(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, cls=DjangoJSONEncoder)


def loads(value: str):
    return json.loads(value)
