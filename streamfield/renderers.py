import warnings
from typing import Optional

from django.core.cache import DEFAULT_CACHE_ALIAS, BaseCache, caches
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import render_to_string

from .options import get_block_opts
from .typing import BlockInstance


class DefaultRenderer:
    @classmethod
    def get_context(cls, block: BlockInstance, **kwargs):
        warnings.warn(
            "get_context() is deprecated in favor of 'make_context'",
            DeprecationWarning,
            stacklevel=2
        )
        return cls.make_context(kwargs, block)

    @classmethod
    def make_context(cls, context: Optional[dict], block: BlockInstance) -> dict:
        return dict(context or {}, **{
            "block": block,
        })

    def __call__(
        self,
        block: BlockInstance,
        context: dict = None,
        request: WSGIRequest = None
    ) -> str:
        opts = get_block_opts(block)
        context = self.make_context(context, block)
        return render_to_string(opts.template, context, request=request, using=opts.engine)


class CacheRenderer(DefaultRenderer):
    """
    Example:
        class HeaderBlock(Model):
            # ...

            class StreamBlockMeta:
                renderer = "streamfield.renderers.CacheRenderer"
                cache_alias = "redis"       # default: 'default'
                cache_ttl = 1800            # default: 3600
    """
    @staticmethod
    def get_cache(
        block: BlockInstance,
        context: dict = None,
        request: WSGIRequest = None
    ) -> BaseCache:
        opts = get_block_opts(block)
        cache_alias = getattr(opts, "cache_alias", DEFAULT_CACHE_ALIAS)
        return caches[cache_alias]

    @staticmethod
    def get_cache_key(
        block: BlockInstance,
        context: dict = None,
        request: WSGIRequest = None
    ) -> str:
        opts = get_block_opts(block)
        return "{}.{}:{}".format(
            opts.app_label,
            opts.model_name,
            block.pk
        )

    @staticmethod
    def get_cache_ttl(
        block: BlockInstance,
        context: dict = None,
        request: WSGIRequest = None
    ) -> str:
        opts = get_block_opts(block)
        return getattr(opts, "cache_ttl", None)

    def __call__(
        self,
        block: BlockInstance,
        context: dict = None,
        request: WSGIRequest = None
    ) -> str:
        opts = get_block_opts(block)
        context = self.make_context(context, block)

        cache = self.get_cache(block, context, request=request)
        cache_key = self.get_cache_key(block, context, request=request)
        cache_ttl = self.get_cache_ttl(block, context, request=request)

        if cache_key in cache:
            return cache.get(cache_key)

        content = render_to_string(opts.template, context, request=request, using=opts.engine)

        if cache_ttl is None:
            cache.set(cache_key, content)
        else:
            cache.set(cache_key, content, cache_ttl)

        return content
