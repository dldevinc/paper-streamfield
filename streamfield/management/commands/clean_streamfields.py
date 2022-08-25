from collections import defaultdict
from typing import List

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from ...field.models import StreamField
from ...models import StreamBlockModel


class Command(BaseCommand):
    help = "Deletes invalid references from stream fields."
    dry_run = False
    known_blocks = set()

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", default=False)

    def fill_known_blocks(self):
        for model in apps.get_models():
            if not issubclass(model, StreamBlockModel):
                continue

            for instance in model._base_manager.iterator():
                record = (
                    instance._meta.app_label,
                    instance._meta.model_name,
                    str(instance.pk)
                )
                self.known_blocks.add(record)

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.fill_known_blocks()

        for model in apps.get_models():
            self.handle_model(model)

    def handle_model(self, model):
        stream_fields = []

        for field in model._meta.get_fields():
            if not isinstance(field, StreamField):
                continue

            stream_fields.append(field.name)

        if stream_fields:
            with transaction.atomic():
                self.clean_model_instances(model, stream_fields)

    def clean_model_instances(self, model, fields: List[str]):
        for instance in model._base_manager.iterator():
            new_values = defaultdict(list)

            for field_name in fields:
                has_changes = False
                invalid_refs = []
                value = getattr(instance, field_name)
                for item in value:
                    record = (
                        item["app_label"],
                        item["model_name"],
                        item["pk"]
                    )

                    if record in self.known_blocks:
                        new_values[field_name].append(item)
                    else:
                        invalid_refs.append(item)
                        has_changes = True

                if not has_changes:
                    del new_values[field_name]
                elif self.dry_run:
                    print(
                        "Invalid references found in object \033[91m{}.{}\033[0m "
                        "with primary key \033[91m{}\033[0m:\n  {}".format(
                            model._meta.app_label,
                            model._meta.model_name,
                            instance.pk,
                            "\n  ".join((repr(ref) for ref in invalid_refs))
                        )
                    )

            if new_values:
                if not self.dry_run:
                    model._base_manager.filter(pk=instance.pk).update(**new_values)
