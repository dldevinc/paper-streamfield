class InvalidStreamTypeError(TypeError):
    pass


class InvalidStreamBlockError(ValueError):
    pass


class SkipBlock(Exception):
    pass
