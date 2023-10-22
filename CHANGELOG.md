# Change Log

## [0.7.1](https://github.com/dldevinc/paper-streamfield/tree/v0.7.1) - 2023-10-22

### Bug fixes

-   The 'verbose_name' of all blocks now starts with a capital letter.

## [0.7.0](https://github.com/dldevinc/paper-streamfield/tree/v0.7.0) - 2023-10-16

### ⚠ BREAKING CHANGES

-   Complete rewrite of block rendering logic.

## [0.6.1](https://github.com/dldevinc/paper-streamfield/tree/v0.6.1) - 2023-10-04

### Bug fixes

-   Use plural model name in lookup dropdown.

## [0.6.0](https://github.com/dldevinc/paper-streamfield/tree/v0.6.0) - 2023-09-29

### ⚠ BREAKING CHANGES

-   Parent context now inherits automatically in block templates. The `parent_context` 
    variable has been removed.

### Features

-   Added the ability to hide certain blocks. 

## [0.5.0](https://github.com/dldevinc/paper-streamfield/tree/v0.5.0) - 2023-06-01

### ⚠ BREAKING CHANGES

-   Added `StreamBlockMeta` class to provide metadata about a stream block.
-   The `admin_block_template` property of the block model has been removed and replaced with 
    `stream_block_template` property of the corresponding `StreamBlockModelAdminMixin`.
-   The `renderer` module was renamed to `renderers`.

## [0.4.0](https://github.com/dldevinc/paper-streamfield/tree/v0.4.0) - 2023-04-16

### ⚠ BREAKING CHANGES

-   Minimum required `paper-admin` version is now `6.0.0`.

## [0.3.0](https://github.com/dldevinc/paper-streamfield/tree/v0.3.0) - 2022-11-30

-   Support for `paper-admin` >= 5.0.
-   Add Python 3.11 support (no code changes were needed, but now we test this release).

## [0.2.1](https://github.com/dldevinc/paper-streamfield/tree/v0.2.1) - 2022-10-05

### Bug fixes

-   Fixed missing static files.

## [0.2.0](https://github.com/dldevinc/paper-streamfield/tree/v0.2.0) - 2022-10-05

### ⚠ BREAKING CHANGES

-   Drop support for django<3.1.
-   Migrating rendering from client-side to server-side.

## [0.1.0](https://github.com/dldevinc/paper-streamfield/tree/v0.1.0) - 2022-09-16

-   First release
