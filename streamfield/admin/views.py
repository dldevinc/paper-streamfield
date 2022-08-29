import json
from json import JSONDecodeError

from django.contrib import admin
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from .. import blocks


@admin.site.admin_view
@csrf_exempt
def render_streamblocks(request):
    try:
        stream = json.loads(request.body)
    except JSONDecodeError:
        return HttpResponseBadRequest()

    if not isinstance(stream, list):
        return HttpResponseBadRequest()

    output = []
    for record in stream:
        block = blocks.from_dict(record)
        model_admin = admin.site._registry[type(block)]
        context = {
            "app_label": record["app_label"],
            "model_name": record["model_name"],
            "instance": block,
            "opts": block._meta,
            "model_admin": model_admin,
            "icon": block._stream_meta.admin_icon,
            "has_view_permission": model_admin.has_view_permission(request, block),
            "has_add_permission": model_admin.has_add_permission(request),
            "has_change_permission": model_admin.has_change_permission(request, block),
            "has_delete_permission": model_admin.has_delete_permission(request, block),
        }
        block_output = render_to_string("streamfield/_block.html", context)
        output.append(block_output)

    return JsonResponse({
        "status": "OK",
        "html": "\n".join(output)
    })