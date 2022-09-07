import json
from json import JSONDecodeError
from typing import Any, Dict, List, Union

from django.contrib.auth import get_permission_codename
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .. import blocks
from ..logging import logger
from ..typing import BlockInstance, BlockModel


class PermissionMixin:
    def has_add_permission(self, model: BlockModel):
        opts = model._meta
        codename = get_permission_codename("add", opts)
        return self.request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, model_or_block: Union[BlockModel, BlockInstance]):
        opts = model_or_block._meta
        codename = get_permission_codename("change", opts)
        return self.request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, model_or_block: Union[BlockModel, BlockInstance]):
        opts = model_or_block._meta
        codename = get_permission_codename("delete", opts)
        return self.request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_view_permission(self, model_or_block: Union[BlockModel, BlockInstance]):
        opts = model_or_block._meta
        codename_view = get_permission_codename("view", opts)
        codename_change = get_permission_codename("change", opts)
        return self.request.user.has_perm(
            "%s.%s" % (opts.app_label, codename_view)
        ) or self.request.user.has_perm(
            "%s.%s" % (opts.app_label, codename_change)
        )


class RenderStreamView(PermissionMixin, View):
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
            logger.warning("Stream is not valid JSON")
            return HttpResponseBadRequest()

        if not isinstance(stream, list):
            logger.warning("Invalid stream type")
            return HttpResponseBadRequest()

        if not all(blocks.is_valid(record) for record in stream):
            logger.warning("Invalid stream value")
            return HttpResponseBadRequest()

        return JsonResponse({
            "blocks": self._render_field(stream)
        })

    def _render_field(self, stream: List) -> str:
        return "\n".join(
            self._render_block(block_data)
            for block_data in stream
        )

    def _render_block(self, record: Dict[str, Any]) -> str:
        try:
            block = blocks.from_dict(record)
        except (LookupError, ObjectDoesNotExist, MultipleObjectsReturned):
            return self._block_invalid(record)
        else:
            return self._block_valid(record, block)

    def _block_valid(self, record: Dict[str, Any], block: BlockInstance) -> str:
        info = (block._meta.app_label, block._meta.model_name)

        context = dict(record, **{
            "title": str(block),
            "description": block._meta.verbose_name,
            "change_related_url": reverse(
                "admin:%s_%s_%s" % (info + ("change",)),
                args=(block.pk,),
            ),
            "can_change_related": self.has_change_permission(block),
            "can_view_related": self.has_view_permission(block),
        })

        return render_to_string("streamfield/_valid_block.html", context)

    def _block_invalid(self, record: Dict[str, Any]) -> str:
        context = dict(record, **{
            "title": _("Invalid block"),
            "description": f"{record['model']} (Primary key: {record['pk']})"
        })
        return render_to_string("streamfield/_invalid_block.html", context)
