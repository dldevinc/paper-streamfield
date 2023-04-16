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
from django.utils.translation import gettext_lazy as _


class HeaderBlock(models.Model):
    text = models.TextField(
        _("text")
    )
    rank = models.PositiveSmallIntegerField(
        _("rank"),
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6)
        ]
    )

    class Meta:
        verbose_name = "Header"

    def __str__(self):
        return Truncator(self.text).chars(64)


class TextBlock(models.Model):
    text = models.TextField(
        _("text")
    )

    class Meta:
        verbose_name = "Text"

    def __str__(self):
        return Truncator(self.text).chars(64)
```

2. Register this models using `StreamBlockModelAdmin` class.

```python
# blocks/admin.py

from django.contrib import admin

from streamfield.admin import StreamBlockModelAdmin

from .models import HeaderBlock, TextBlock


@admin.register(HeaderBlock)
class HeaderBlockAdmin(StreamBlockModelAdmin):
    list_display = ["__str__", "rank"]


@admin.register(TextBlock)
class TextBlockAdmin(StreamBlockModelAdmin):
    pass
```

3. Create templates for each block model, named as lowercase
   model name or _snake_cased_ model name.

```html
<!-- blocks/templates/blocks/headerblock.html -->
<!-- or -->
<!-- blocks/templates/blocks/header_block.html -->
<h{{ block.rank }}>{{ block.text }}</h{{ block.rank }}>
```

```html
<!-- blocks/templates/blocks/textblock.html -->
<!-- or -->
<!-- blocks/templates/blocks/text_block.html -->
<div>{{ block.text|linebreaks }}</div>
```

You can also use the `block_template` option to specify the template to use:

```python
class HeaderBlock(models.Model):
    block_template = "blocks/header.html"
    ...
```

4. Add `StreamField` to your model:

```python
# app/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

from streamfield.field.models import StreamField


class Page(models.Model):
    stream = StreamField(_("stream"), models=[
        "blocks.HeaderBlock",
        "blocks.TextBlock",
    ])

    class Meta:
        verbose_name = "Page"
```

Result:
![](https://user-images.githubusercontent.com/6928240/190413272-14b95712-de0f-4a9b-a815-40e3fb0a2d85.png)

Now you can create some blocks:
![](https://user-images.githubusercontent.com/6928240/190414025-dfe364a9-524e-4529-835d-a3e507d1ee19.png)

5. Use `render_stream` templatetag to render the stream field.

```html
<!-- app/templates/index.html -->
{% load streamfield %} {% render_stream page.stream %}
```

Result:
![](https://user-images.githubusercontent.com/6928240/190416377-e2ba504f-8aa0-44ed-b59d-0cf1ccea695e.png)

## Special cases

### Use another template engine

You can specify a template engine to render a specific block with
`block_template_engine` option:

```python
class HeaderBlock(models.Model):
    block_template = "blocks/header.html"
    block_template_engine = "jinja2"
    ...
```

### Add extra context to blocks

You can add additional variables by passing keyword arguments to the `render_stream` templatetag:

```html
<!-- app/templates/index.html -->
{% load streamfield %} {% render_stream page.stream css_class="red" %}
```

```html
<!-- text_block.html -->
<div class="{{ css_class }}">{{ block.text|linebreaks }}</div>
```

### Access parent context from within a block

The parent context can be accessed via a `parent_context` variable:

```html
<!-- app/templates/index.html -->
{% load streamfield %} {% with css_class="blue" %} {% render_stream page.stream %} {% endwith %}
```

```html
<!-- text_block.html -->
<div class="{{ parent_context.css_class }}">{{ block.text|linebreaks }}</div>
```
