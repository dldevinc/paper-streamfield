from unittest.mock import Mock


def get_mock(*args, **kwargs) -> Mock:
    mock = Mock(*args, **kwargs)
    mock.side_effect = lambda: mock
    return mock
