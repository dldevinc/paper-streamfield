# paper-streamfield

Implementation of the Wagtail's StreamField block picker for paper-admin.

[![PyPI](https://img.shields.io/pypi/v/paper-streamfield.svg)](https://pypi.org/project/paper-streamfield/)
[![Build Status](https://github.com/dldevinc/paper-streamfield/actions/workflows/tests.yml/badge.svg)](https://github.com/dldevinc/paper-streamfield)
[![Software license](https://img.shields.io/pypi/l/paper-streamfield.svg)](https://pypi.org/project/paper-streamfield/)

## Compatibility

-   `python` >= 3.9
-   `django` >= 3.1
-   `paper-admin` >= 6.0

## Installation

Install the latest release with pip:

```shell
pip install paper-streamfield
```

Add `streamfield` to your INSTALLED_APPS in django's `settings.py`:

```python
INSTALLED_APPS = (
    # other apps
    "streamfield",
)
```

Add `streamfield.urls` to your URLconf:

```python
urlpatterns = patterns('',
    ...
    path("streamfields/", include("streamfield.urls")),
)
```

## How to use

1. Create some models that you want to use as blocks:

   ```python
   # blocks/models.py
   
   from django.core.validators import MaxValueValidator, MinValueValidator
   from django.db import models
   from django.utils.text import Truncator
   
   
   class HeadingBlock(models.Model):
       text = models.TextField()
       rank = models.PositiveSmallIntegerField(
           default=1,
           validators=[
               MinValueValidator(1),
               MaxValueValidator(6)
           ]
       )
   
       class Meta:
           verbose_name = "Heading"
   
       def __str__(self):
           return Truncator(self.text).chars(128)
   
   
   class TextBlock(models.Model):
       text = models.TextField()
   
       class Meta:
           verbose_name = "Text"
   
       def __str__(self):
           return Truncator(self.text).chars(128)
   ```

2. Register your models using `StreamBlockModelAdmin` class.

   ```python
   # blocks/admin.py
   
   from django.contrib import admin
   from streamfield.admin import StreamBlockModelAdmin
   from .models import HeadingBlock, TextBlock
   
   
   @admin.register(HeadingBlock)
   class HeadingBlockAdmin(StreamBlockModelAdmin):
       list_display = ["__str__", "rank"]
   
   
   @admin.register(TextBlock)
   class TextBlockAdmin(StreamBlockModelAdmin):
       pass
   ```

3. Create templates for each block model, named as lowercase
   model name or _snake_cased_ model name.

   ```html
   <!-- blocks/templates/blocks/headingblock.html -->
   <!-- or -->
   <!-- blocks/templates/blocks/heading_block.html -->
   <h{{ block.rank }}>{{ block.text }}</h{{ block.rank }}>
   ```
   
   ```html
   <!-- blocks/templates/blocks/textblock.html -->
   <!-- or -->
   <!-- blocks/templates/blocks/text_block.html -->
   <div>{{ block.text|linebreaks }}</div>
   ```

4. Add a `StreamField` to your model:

   ```python
   # app/models.py
   
   from django.db import models
   from django.utils.translation import gettext_lazy as _
   from streamfield.field.models import StreamField
   
   
   class Page(models.Model):
       stream = StreamField(
          _("stream"), 
          models=[
              "blocks.HeaderBlock",
              "blocks.TextBlock",
          ]
       )
   
       class Meta:
           verbose_name = "Page"
   ```
   
   Result:
   ![](https://user-images.githubusercontent.com/6928240/190413272-14b95712-de0f-4a9b-a815-40e3fb0a2d85.png)
   
   Now you can create some blocks:
   ![](https://user-images.githubusercontent.com/6928240/190414025-dfe364a9-524e-4529-835d-a3e507d1ee19.png)

5. Use `render_stream` template tag to render the stream field.

   ```html
   <!-- app/templates/index.html -->
   {% load streamfield %}
   
   {% render_stream page.stream %}
   ```
   
   Result:
   ![](https://user-images.githubusercontent.com/6928240/190416377-e2ba504f-8aa0-44ed-b59d-0cf1ccea695e.png)


> When working with block templates, it's important to note that 
> you have access to all variables from the parent context.

## Special cases

### Use custom template name or template engine

You can specify a template name or engine to render a specific block 
with `StreamBlockMeta` class in your block model:

```python
class HeadingBlock(models.Model):
    # ...

    class StreamBlockMeta:
        template_engine = "jinja2"
        template_name = "blocks/heading.html"
```

### Caching the rendered HTML of a block

You can enable caching for specific blocks to optimize rendering.

```python
class HeadingBlock(models.Model):
    # ...

    class StreamBlockMeta:
        cache = True
        cache_ttl = 3600
```

Once caching is enabled for the block, the rendered HTML will be stored 
in cache, and subsequent requests will retrieve the cached content, 
reducing the need for re-rendering.

> Note that the specified block will **not** be invalidated
> when something changes in it.

### Adding context variables to all blocks

You can add context variables to all blocks in your StreamField by providing them 
through the `render_stream` template tag. This allows you to pass common context data 
to customize the rendering of all content blocks consistently:

```html
<!-- app/templates/index.html -->
{% load streamfield %}

{% render_stream page.stream classes="text text--small" %}
```

```html
<!-- blocks/templates/blocks/textblock.html -->
<div class="{{ classes }}">{{ block.text|linebreaks }}</div>
```

### Adding context variables to a specific block

To add context variables to a specific content block, 
you must create a custom processor. A processor provides a mechanism for 
customizing the context data and the rendering process of an individual block.

1. Create a custom processor class that inherits from 
   `streamfield.processors.DefaultProcessor`.
   ```python
   from streamfield.processors import DefaultProcessor
   from reviews.models import Review

   class ReviewsBlockProcessor(DefaultProcessor):
       def get_context(self, block):
           context = super().get_context(block)
           context["reviews"] = Review.objects.all()[:5]
           return context
   ```
2. In your block's model, specify the processor to use:
   ```python
   class ReviewsBlock(models.Model):
       # ...
    
       class StreamBlockMeta:
           processor = "your_app.processors.ReviewsBlockProcessor"
   ```

You can utilize the `exceptions.SkipBlock` feature to conditionally skip the rendering 
of a block. This can be useful, for example, when dealing with a block like "Articles" 
that should only render when there are articles available. Example:

```python
from streamfield.processors import DefaultProcessor
from streamfield.exceptions import SkipBlock
from articles.models import Article


class ArticlesBlockProcessor(DefaultProcessor):
    def get_context(self, block):
        context = super().get_context(block)

        articles = Article.object.all()[:3]
        if len(articles) < 3:
            # Skip block if not enough article instances
            raise SkipBlock

        context["articles"] = articles
        return context
```

### Using `render_block` template tag

In some cases, you may have a page that references a specific block through 
a `ForeignKey` relationship, and you want to render that referenced block on the page. 
You can achieve this using the render_block template tag. Here's an example:

```python
# page/models.py

from django.db import models
from blocks.models import TextBlock

class Page(models.Model):
   text_block = models.ForeignKey(TextBlock, on_delete=models.SET_NULL, blank=True, null=True)

   class Meta:
      verbose_name = "Page"
```

```html
<!-- app/templates/page.html -->
{% load streamfield %}

<div>
    <h1>Page Title</h1>
    <div>
        <h2>Text Block:</h2>
        {% render_block page.text_block %}
    </div>
</div>
```

### Customize block in admin interface

You can customize how a block is rendered in the admin interface
by specifying `stream_block_template` field in the `StreamBlockModelAdmin`
class:

```python
from django.contrib import admin
from streamfield.admin import StreamBlockModelAdmin
from .models import ImageBlock


@admin.register(ImageBlock)
class ImageBlockAdmin(StreamBlockModelAdmin):
    stream_block_template = "blocks/admin/image.html"
    list_display = ["__str__", "title", "alt"]
```

```html
<!-- blocks/admin/image.html -->
{% extends "streamfield/admin/block.html" %}

{% block content %}
   <div class="d-flex">
      <div class="flex-grow-0 mr-2">
         <img class="preview"
              src="{{ instance.image }}"
              width="48"
              height="36"
              title="{{ instance.title }}"
              alt="{{ instance.alt }}"
              style="object-fit: cover">
      </div>
   
      {{ block.super }}
   </div>
{% endblock content %}
```

## Settings

`PAPER_STREAMFIELD_DEFAULT_PROCESSOR`<br>
Default processor for content blocks.<br>
Default: `"streamfield.processors.DefaultProcessor"`

`PAPER_STREAMFIELD_DEFAULT_TEMPLATE_ENGINE`<br>
Default template engine for `render_stream` template tag.<br>
Default: `None`
