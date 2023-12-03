from typing import Any

from django.db import models

BlockModel = type[models.Model]
BlockInstance = models.Model
TemplateContext = dict[str, Any]
