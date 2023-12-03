from app.models import Advantage
from streamfield import exceptions, processors


class AdvantagesBlockProcessor(processors.DefaultProcessor):
    def get_context(self, block):
        context = super().get_context(block)

        advantages = Advantage.objects.all()[:3]
        if len(advantages) < 3:
            raise exceptions.SkipBlock

        context["advantages"] = advantages
        return context
