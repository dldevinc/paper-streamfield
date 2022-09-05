import json
from json import JSONDecodeError
from typing import Any, Dict, List

from django.contrib import admin
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .. import blocks
from ..typing import BlockInstance


class RenderFieldView(View):
    """
    Отрисовка поля StreamField в соответствии с переданными JSON-данными.
    """
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
            "rendered_field": self._render_field(stream)
        })

    def _render_field(self, stream: List) -> str:
        return "\n".join(
            self._render_block(block_data)
            for block_data in stream
        )

    def _render_block(self, block_data: Dict[str, Any]) -> str:
        block_instance = blocks.from_dict(block_data)
        if block_instance is None:
            return self._render_invalid_block(block_data)
        else:
            return self._render_valid_block(block_data, block_instance)

    def _render_valid_block(self, block_data: Dict[str, Any], block: BlockInstance) -> str:
        model_admin = admin.site._registry[type(block)]
        info = (block._meta.app_label, block._meta.model_name)

        change_related_url = reverse(
            "admin:%s_%s_%s" % (info + ("change",)),
            current_app=model_admin.admin_site.name,
            args=(block.pk, ),
        )

        return render_to_string("streamfield/_valid_block.html", {
            "uuid": block_data["uuid"],
            "instance": block,
            "opts": block._meta,
            "can_add_related": model_admin.has_add_permission(self.request),
            "can_change_related": model_admin.has_change_permission(self.request, block),
            "change_related_url": change_related_url,
            "can_delete_related": model_admin.has_delete_permission(self.request, block),
            "can_view_related": model_admin.has_view_permission(self.request, block),
        })

    def _render_invalid_block(self, block_data: Dict[str, Any]) -> str:
        return render_to_string("streamfield/_invalid_block.html", {
            "uuid": block_data["uuid"],
            "pk": block_data["pk"],
            "app_label": block_data["app_label"],
            "model_name": block_data["model_name"],
        })
