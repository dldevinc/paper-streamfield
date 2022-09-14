from streamfield import utils


class TestSnakeCase:
    def test_single_word(self):
        assert utils.camel_case_to_snake_case("Header") == "header"

    def test_camel_case(self):
        assert utils.camel_case_to_snake_case("HeaderBlockGSM") == "header_block_gsm"

    def test_snake_case(self):
        assert utils.camel_case_to_snake_case("header_block") == "header_block"
