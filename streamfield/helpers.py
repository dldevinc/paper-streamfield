import json
from typing import Dict, List, Union

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest

from . import blocks, exceptions
from .logging import logger


def render_stream(stream: Union[str, List], context: Dict = None, request: WSGIRequest = None) -> str:
    """
    Отрисовка всех блоков из JSON-массива.
    """
    if isinstance(stream, str):
        stream = json.loads(stream)

    if not isinstance(stream, list):
        raise exceptions.InvalidStreamTypeError(stream)

    output = []
    for record in stream:
        if not blocks.is_valid(record):
            raise exceptions.InvalidStreamBlockError(record)

        try:
            block = blocks.from_dict(record)
        except (LookupError, ObjectDoesNotExist, MultipleObjectsReturned):
            logger.warning("Invalid block: %r", record)
            continue
        else:
            output.append(
                blocks.render(
                    block,
                    context or {},
                    request=request,
                )
            )

    return "\n".join(output)
