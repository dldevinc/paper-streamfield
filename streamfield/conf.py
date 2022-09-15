from django.conf import settings

DEFAULT_RENDERER = getattr(settings, "PAPER_STREAMFIELD_DEFAULT_RENDERER", "streamfield.renderer.render_template")
DEFAULT_TEMPLATE_ENGINE = getattr(settings, "PAPER_STREAMFIELD_DEFAULT_TEMPLATE_ENGINE", None)
