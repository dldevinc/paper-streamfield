import json
from json import JSONDecodeError
from typing import Any, Dict, List

from django.apps import apps
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


class Http400(Exception):
    pass


class AdminStreamViewMixin:
    admin_site = None

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http400 as exc:
            message = exc.args[0] if exc.args else ""
            logger.warning(message)
            return HttpResponseBadRequest(message)

    def parse_request_json(self):
        try:
            return json.loads(self.request.body)
        except JSONDecodeError:
            raise Http400(_("The request body is not valid JSON"))

    def get_model_admin(self, model: BlockModel):
        """
        :rtype: django.contrib.admin.ModelAdmin | None
        """
        if model not in self.admin_site._registry:
            return None
        return self.admin_site._registry[model]


class RenderStreamView(AdminStreamViewMixin, View):
    def post(self, request):
        data = self.parse_request_json()

        try:
            allowed_models = data["allowedModels"]
            stream = data["value"]
        except KeyError:
            raise Http400(_("Invalid request data"))

        if not isinstance(stream, list):
            raise Http400(_("Invalid stream type"))

        return JsonResponse({
            "blocks": "".join(
                self.render_block(record, allowed_models)
                for record in stream
            )
        })

    def render_block(self, record: Dict[str, Any], allowed_models: List["str"]) -> str:
        if not blocks.is_valid(record):
            return self.block_invalid(record, _("Invalid data format"))

        if record["model"] not in allowed_models:
            return self.block_invalid(record, _("The specified class is not allowed here"))

        try:
            block = blocks.from_dict(record)
        except LookupError:
            return self.block_invalid(record, _("Model not found"))
        except ObjectDoesNotExist:
            return self.block_invalid(record, _("Instance not found"))
        except MultipleObjectsReturned:
            return self.block_invalid(record, _("Multiple objects returned"))
        else:
            return self.block_valid(record, block)

    def block_valid(self, record: Dict[str, Any], block: BlockInstance) -> str:
        model_admin = self.get_model_admin(type(block))
        template = getattr(model_admin, "stream_block_template")
        return render_to_string(template, {
            "uuid": record["uuid"],
            "instance": block,
            "opts": block._meta,
            "has_change_permission": model_admin.has_change_permission(self.request, block) if model_admin is not None else False,
            "has_view_permission": model_admin.has_view_permission(self.request, block) if model_admin is not None else False,
        }, request=self.request)

    def block_invalid(self, record: Dict[str, Any], reason: str) -> str:
        return render_to_string("streamfield/admin/invalid_block.html", {
            "uuid": record.get("uuid", ""),
            "model": record.get("model", "undefined"),
            "pk": record.get("pk", "undefined"),
            "reason": reason,
        }, request=self.request)


class RenderButtonsView(AdminStreamViewMixin, View):
    def post(self, request):
        data = self.parse_request_json()

        try:
            allowed_models = data["allowedModels"]
            field_id = data["field_id"]
        except KeyError:
            raise Http400(_("Invalid request data"))

        if not isinstance(allowed_models, list):
            raise Http400(_("Invalid request data"))

        if not all(isinstance(item, str) for item in allowed_models):
            raise Http400(_("Invalid request data"))

        creatable_models = []
        searchable_models = []

        for model_name in allowed_models:
            try:
                model = apps.get_model(model_name)  # type: BlockModel
            except LookupError:
                continue

            model_admin = self.get_model_admin(model)
            if model_admin is None:
                continue

            info = (model._meta.app_label, model._meta.model_name)
            has_add_permission = model_admin.has_add_permission(self.request)
            has_change_permission = model_admin.has_change_permission(self.request)
            has_view_permission = model_admin.has_view_permission(self.request)

            if has_add_permission:
                creatable_models.append({
                    "id": "add_%s--%s.%s" % (field_id, info[0], info[1]),
                    "title": model._meta.verbose_name,
                    "url": reverse("admin:%s_%s_add" % info),
                    "action": "create",
                })

            if has_change_permission or has_view_permission:
                searchable_models.append({
                    "id": "lookup_%s--%s.%s" % (field_id, info[0], info[1]),
                    "title": model._meta.verbose_name,
                    "url": reverse("admin:%s_%s_changelist" % info),
                    "action": "lookup",
                })

        return JsonResponse({
            "buttons": render_to_string("streamfield/admin/buttons.html", {
                "creatable_models": creatable_models,
                "searchable_models": searchable_models,
            }, request=self.request)
        })
