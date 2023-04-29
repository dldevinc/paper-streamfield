from django.core.cache import DEFAULT_CACHE_ALIAS, BaseCache, caches
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import render_to_string

from .options import get_block_opts
from .typing import BlockInstance


class DefaultRenderer:
    @staticmethod
    def get_context(block: BlockInstance, **kwargs):
        context = {
            "block": block,
        }
        context.update(kwargs)
        return context

    def __call__(
        self,
        block: BlockInstance,
        request: WSGIRequest = None,
        **kwargs
    ) -> str:
        opts = get_block_opts(block)
        context = self.get_context(block, **kwargs)
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
        request: WSGIRequest = None,
        **kwargs
    ) -> BaseCache:
        opts = get_block_opts(block)
        cache_alias = getattr(opts, "cache_alias", DEFAULT_CACHE_ALIAS)
        return caches[cache_alias]

    @staticmethod
    def get_cache_key(
        block: BlockInstance,
        request: WSGIRequest = None,
        **kwargs
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
        request: WSGIRequest = None,
        **kwargs
    ) -> str:
        opts = get_block_opts(block)
        return getattr(opts, "cache_ttl", None)

    def __call__(
        self,
        block: BlockInstance,
        request: WSGIRequest = None,
        **kwargs
    ) -> str:
        cache = self.get_cache(block, request=request, **kwargs)
        cache_key = self.get_cache_key(block, request=request, **kwargs)
        cache_ttl = self.get_cache_ttl(block, request=request, **kwargs)

        if cache_key in cache:
            return cache.get(cache_key)

        content = super().__call__(block, request=request, **kwargs)

        if cache_ttl is None:
            cache.set(cache_key, content)
        else:
            cache.set(cache_key, content, cache_ttl)

        return content
