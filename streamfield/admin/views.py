import json
from json import JSONDecodeError
from typing import Dict

from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .. import blocks
from ..typing import BlockInstance


class RenderFieldView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            stream = json.loads(request.body)
        except JSONDecodeError:
            return HttpResponseBadRequest()

        if not isinstance(stream, list):
            return HttpResponseBadRequest()

        return JsonResponse({
            "html": "\n".join(
                self._render_block(block_data)
                for block_data in stream
            )
        })

    def _render_block(self, block_data: Dict) -> str:
        block_instance = blocks.from_dict(block_data)
        if block_instance is None:
            return self._render_invalid_block(block_data)
        else:
            return self._render_valid_block(block_data, block_instance)

    def _render_valid_block(self, block_data: Dict, block: BlockInstance) -> str:
        # model_admin = admin.site._registry[type(block)]
        return render_to_string("streamfield/_valid_block.html", {
            "uuid": block_data["uuid"],
            "instance": block,
            "opts": block._meta,
            # "has_view_permission": model_admin.has_view_permission(request, block),
            # "has_add_permission": model_admin.has_add_permission(request),
            # "has_change_permission": model_admin.has_change_permission(request, block),
            # "has_delete_permission": model_admin.has_delete_permission(request, block),
        })

    def _render_invalid_block(self, block_data: Dict) -> str:
        return render_to_string("streamfield/_invalid_block.html", {
            "uuid": block_data["uuid"],
            "pk": block_data["pk"],
            "app_label": block_data["app_label"],
            "model_name": block_data["model_name"],
        })
