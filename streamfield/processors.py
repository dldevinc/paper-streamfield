from collections.abc import Iterable

from django.apps import apps
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.template.loader import render_to_string

from .conf import DEFAULT_TEMPLATE_ENGINE
from .utils import camel_case_to_snake_case


class BaseProcessor:
    def __init__(self, app_label, model_name, **kwargs):
        for key, value in kwargs.items():
            if not key.startswith("_") and key != "processor":
                setattr(self, key, value)

        self.app_label = app_label
        self.model_name = model_name
        self.model = apps.get_model(self.app_label, self.model_name)

    def get_queryset(self):
        """
        Get a QuerySet for retrieving content blocks of the specified model.

        This method generates a QuerySet for retrieving content blocks
        of a specific model. It allows for the selection of related objects
        based on the provided `select_related` attribute. The resulting QuerySet
        will be used to query the database and fetch content blocks.

        :rtype: django.db.models.QuerySet
        """
        raise NotImplementedError

    def get_context(self, block):
        """
        Get the context data for rendering a content block.

        This method generates a dictionary containing the context data
        used during the rendering of a content block. It typically includes
        information related to the content block itself.

        :type block: django.db.models.Model
        :rtype: dict
        """
        raise NotImplementedError

    def get_template_names(self, block):
        """
        Get a list of template names to be used for rendering
        the content block.

        :type block: django.db.models.Model
        :rtype: str|list[str]|tuple[str]
        """
        raise NotImplementedError

    def render(self, block, context=None, request=None):
        """
        This method takes a content block model instance,
        processes it, and renders it as HTML.

        :type block: django.db.models.Model
        :type context: dict|None
        :type request: django.core.handlers.wsgi.WSGIRequest
        :rtype: str
        """
        raise NotImplementedError


class DefaultProcessor(BaseProcessor):
    select_related = None
    template_engine = DEFAULT_TEMPLATE_ENGINE
    template_name = None
    cache = False
    cache_alias = DEFAULT_CACHE_ALIAS
    cache_ttl = 3600

    def get_queryset(self):
        queryset = self.model._default_manager.all()
        if isinstance(self.select_related, str):
            queryset = queryset.select_related(self.select_related)
        elif isinstance(self.select_related, Iterable):
            queryset = queryset.select_related(*self.select_related)
        return queryset

    def get_context(self, block):
        return {
            "block": block
        }

    def get_template_names(self, block):
        return self.template_name or (
            "%s/%s.html" % (self.app_label, self.model_name.lower()),
            "%s/%s.html" % (self.app_label, camel_case_to_snake_case(self.model_name)),
        )

    def render(self, block, context=None, request=None):
        extra_context = self.get_context(block)
        context = dict(context or {}, **(extra_context or {}))
        template_names = self.get_template_names(block)

        if not self.cache:
            return render_to_string(
                template_names,
                context=context,
                request=request,
                using=self.template_engine
            )

        cache = caches[self.cache_alias]
        cache_key = self.get_cache_key(block)
        if cache_key in cache:
            return cache.get(cache_key)

        content = render_to_string(
            template_names,
            context=context,
            request=request,
            using=self.template_engine
        )

        cache_ttl = self.get_cache_ttl(block)
        if cache_ttl is None:
            cache.set(cache_key, content)
        else:
            cache.set(cache_key, content, cache_ttl)

        return content

    def get_cache_key(self, block):
        """
        Generate a cache key for a content block.

        This method creates a unique cache key for a content block
        using the application label, model name, and the block's primary key (pk).
        The cache key is used to store and retrieve content blocks from cache,
        allowing for efficient caching of rendered content.

        :type block: django.db.models.Model
        :rtype: str
        """
        return "{}.{}:{}".format(
            self.app_label,
            self.model_name,
            block.pk
        )

    def get_cache_ttl(self, block):
        """
        Get the cache time-to-live (TTL) for a content block.

        This method retrieves the cache time-to-live (TTL) value
        for a specific content block. The TTL determines how long
        the rendered content block will be cached before it expires
        and is refreshed.

        :type block: django.db.models.Model
        :rtype: int
        """
        return self.cache_ttl
