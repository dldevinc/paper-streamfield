# paper-streamfield

Implementation of the Wagtail's StreamField block picker for paper-admin.

[![PyPI](https://img.shields.io/pypi/v/paper-streamfield.svg)](https://pypi.org/project/paper-streamfield/)
[![Build Status](https://github.com/dldevinc/paper-streamfield/actions/workflows/tests.yml/badge.svg)](https://github.com/dldevinc/paper-streamfield)
[![Software license](https://img.shields.io/pypi/l/paper-streamfield.svg)](https://pypi.org/project/paper-streamfield/)

## Compatibility

-   `python` >= 3.8
-   `django` >= 2.2
-   `paper-admin` >= 4.1

## Installation

Install the latest release with pip:

```shell
pip install paper-streamfield[orjson]
```

Add `streamfield` to your INSTALLED_APPS in django's `settings.py`:

```python
INSTALLED_APPS = (
    # other apps
    "streamfield",
)
```
