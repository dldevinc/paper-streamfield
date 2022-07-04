import uuid
import datetime
from streamfield.serialization import json, orjson


class TestSerialization:
    def test_uuid(self):
        value = uuid.uuid4()
        assert json.dumps(value) == orjson.dumps(value)

    def test_datetime(self):
        value = datetime.datetime.now()
        assert json.dumps(value) == orjson.dumps(value)[:-4] + '"'  # truncate microseconds

    def test_non_ascii(self):
        value = "Привет"
        assert json.dumps(value) == orjson.dumps(value)
