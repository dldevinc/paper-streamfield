from django.utils.module_loading import import_string

from .typing import RenderFuncCallable


def import_render_func(value: str) -> RenderFuncCallable:
    """
    Импортирует функцию отрисовки блока из строкового представления
    (пример: "app.views.render_header").
    """
    render_func = import_string(value)
    if not callable(render_func):
        raise ImportError("%s object is not callable" % value)
    return render_func
