from django.utils.regex_helper import _lazy_re_compile
re_camel_case = _lazy_re_compile(r"(((?<=[a-z])[A-Z])|((?<!^)[A-Z](?![A-Z]|$)))")


def camel_case_to_snake_case(value):
    return re_camel_case.sub(r"_\1", value).lower()
