from .registry import registry as default_registry


def streamblock(*, _registry=default_registry, **options):
    """
    Декоратор, помечающий модель как модель блока, делая возможным
    добавление экземпляров этой модели в StreamField.
    """
    def inner(model):
        _registry.register(model, **options)
        return model
    return inner
