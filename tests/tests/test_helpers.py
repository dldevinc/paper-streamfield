from streamfield import helpers


class TestHelpers:
    def test_get_streamblocks_models(self):
        blocks = helpers.get_streamblocks_models()
        assert len(blocks) == 3
