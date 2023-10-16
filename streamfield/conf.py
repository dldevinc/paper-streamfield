from django.conf import settings

DEFAULT_TEMPLATE_ENGINE = getattr(settings, "PAPER_STREAMFIELD_DEFAULT_TEMPLATE_ENGINE", None)
DEFAULT_PROCESSOR = getattr(settings, "PAPER_STREAMFIELD_DEFAULT_PROCESSOR", "streamfield.processors.DefaultProcessor")
