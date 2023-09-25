# paper-streamfield

Implementation of the Wagtail's StreamField block picker for paper-admin.

[![PyPI](https://img.shields.io/pypi/v/paper-streamfield.svg)](https://pypi.org/project/paper-streamfield/)
[![Build Status](https://github.com/dldevinc/paper-streamfield/actions/workflows/tests.yml/badge.svg)](https://github.com/dldevinc/paper-streamfield)
[![Software license](https://img.shields.io/pypi/l/paper-streamfield.svg)](https://pypi.org/project/paper-streamfield/)

## Compatibility

-   `python` >= 3.8
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

## Special cases

### Use custom template name or template engine

If you need to use custom template name or template engine, you can
specify 

You can specify a template name or engine to render a specific block 
with `StreamBlockMeta` class in your block model:

```python
class HeadingBlock(models.Model):
    # ...

    class StreamBlockMeta:
        engine = "jinja2"
        template = "blocks/heading.html"
```

### Add extra context

You can add extra context to the template by passing
additional keyword arguments to `render_stream` template tag:

```html
<!-- blocks/templates/blocks/textblock.html -->
<div class="{{ classes }}">{{ block.text|linebreaks }}</div>
```

```html
<!-- app/templates/index.html -->
{% load streamfield %}

{% render_stream page.stream classes="text text--small" %}
```

### Access parent context from within a block

In some cases you need to access the parent context from the block
template.

You can access the parent context from the block template by using
`parent_context` variable:

```html
<!-- blocks/templates/blocks/textblock.html -->
<div class="{{ parent_context.classes }}">{{ block.text|linebreaks }}</div>
```

```html
<!-- app/templates/index.html -->
{% load streamfield %}

<!-- Add classes to the page context -->
{% with classes="text text--small" %}
  {% render_stream page.stream %}
{% endwith %}
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

### Caching the rendered HTML of a block

You can cache the rendered HTML of a block by using `CacheRenderer`
class:

```python
class HeadingBlock(models.Model):
    # ...

    class StreamBlockMeta:
        renderer = "streamfield.renderers.CacheRenderer"
        cache_ttl = 3600
```

> Note that the specified block will **not** be invalidated 
> when something changes in it.

## Settings

`PAPER_STREAMFIELD_DEFAULT_RENDERER`<br>
Default renderer for `render_stream` template tag.<br>
Default: `"streamfield.renderers.DefaultRenderer"`

`PAPER_STREAMFIELD_DEFAULT_TEMPLATE_ENGINE`<br>
Default template engine for `render_stream` template tag.<br>
Default: `None`
