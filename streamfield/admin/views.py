import json
from json import JSONDecodeError
from typing import Any, Dict, Union

from django.apps import apps
from django.contrib.auth import get_permission_codename
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .. import blocks, conf
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
            return HttpResponseBadRequest("Stream is not valid JSON")

        if not isinstance(stream, list):
            logger.warning("Invalid stream type")
            return HttpResponseBadRequest("Invalid stream type")

        return JsonResponse({
            "blocks": "".join(
                self.render_block(block_data)
                for block_data in stream
            )
        })

    def render_block(self, record: Dict[str, Any]) -> str:
        if not blocks.is_valid(record):
            return self.block_invalid(record)

        try:
            block = blocks.from_dict(record)
        except (LookupError, ObjectDoesNotExist, MultipleObjectsReturned):
            return self.block_invalid(record)
        else:
            return self.block_valid(record, block)

    def block_valid(self, record: Dict[str, Any], block: BlockInstance) -> str:
        info = (block._meta.app_label, block._meta.model_name)
        has_change_permission = self.has_change_permission(block)
        has_view_permission = self.has_view_permission(block)

        admin_template = getattr(block, "admin_block_template", conf.DEFAULT_ADMIN_BLOCK_TEMPLATE)
        return render_to_string(admin_template, {
            "uuid": record["uuid"],
            "model": record["model"],
            "pk": record["pk"],
            "title": str(block),
            "verbose_name": block._meta.verbose_name,
            "change_button": {
                "show": has_change_permission or has_view_permission,
                "title": _("Change block") if has_change_permission else _("View block"),
                "icon": "fa-pencil" if has_change_permission else "fa-eye",
                "url": reverse(
                    "admin:%s_%s_%s" % (info + ("change",)),
                    args=(block.pk,),
                ),
            },
            "delete_button": {
                "title": _("Delete block"),
                "icon": "fa-trash"
            },
        }, request=self.request)

    def block_invalid(self, record: Dict[str, Any]) -> str:
        model = record.get("model", "undefined")
        pk = record.get("pk", "undefined")
        return render_to_string("streamfield/admin/invalid_block.html", {
            "uuid": record.get("uuid", ""),
            "model": model,
            "pk": pk,
            "title": _("Invalid block"),
            "delete_button": {
                "title": _("Delete block"),
                "icon": "fa-trash"
            },
        }, request=self.request)


class RenderToolbarView(PermissionMixin, View):
    """
    Проверка прав на переданные модели для отрисовки кнопок StreamField.
    """
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            logger.warning("Request is not valid JSON")
            return HttpResponseBadRequest()

        try:
            models = data["models"]
            field_id = data["field_id"]
        except KeyError:
            logger.warning("Invalid request body")
            return HttpResponseBadRequest("Invalid request body")

        if not isinstance(models, list):
            logger.warning("Invalid request body")
            return HttpResponseBadRequest("Invalid request body")

        if not all(isinstance(item, str) for item in models):
            logger.warning("Invalid request body")
            return HttpResponseBadRequest("Invalid request body")

        creatable_models = []
        searchable_models = []

        for model_name in models:
            try:
                model = apps.get_model(model_name)  # type: BlockModel
            except LookupError:
                continue

            info = (model._meta.app_label, model._meta.model_name)

            if self.has_add_permission(model):
                creatable_models.append({
                    "id": "add_%s--%s.%s" % (field_id, info[0], info[1]),
                    "title": model._meta.verbose_name,
                    "url": reverse("admin:%s_%s_add" % info),
                    "action": "create",
                })

            if self.has_change_permission(model) or self.has_view_permission(model):
                searchable_models.append({
                    "id": "lookup_%s--%s.%s" % (field_id, info[0], info[1]),
                    "title": model._meta.verbose_name,
                    "url": reverse("admin:%s_%s_changelist" % info),
                    "action": "lookup",
                })

        return JsonResponse({
            "toolbar": render_to_string("streamfield/admin/toolbar.html", {
                "creatable_models": creatable_models,
                "searchable_models": searchable_models,
            }, request=self.request)
        })
