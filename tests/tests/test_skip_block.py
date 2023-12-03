from uuid import uuid4

import pytest
from blocks.models import AdvantagesBlock, HeaderBlock, TextBlock

from app.models import Advantage
from streamfield import helpers


@pytest.mark.django_db
class TestSkippableBlock:
    def test_rendering(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        TextBlock.objects.create(
            pk=1,
            text="Lorem ipsum dolor sit amet, consectetur adipisicing elit."
        )

        AdvantagesBlock.objects.create(
            pk=1,
        )

        Advantage.objects.create(
            pk=1,
            title="Comfort Redefined",
            description="Ergonomic design for fatigue-free hours of work."
        )
        Advantage.objects.create(
            pk=2,
            title="Precision in Action",
            description="Navigate tasks with precise tracking and responsive controls."
        )
        Advantage.objects.create(
            pk=3,
            title="Unleash Wireless Freedom",
            description="Experience unrestricted movement with our wireless technology."
        )

        stream = [{
            "uuid": str(uuid4()),
            "model": "blocks.headerblock",
            "pk": "1",
            "visible": True
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.advantagesblock",
            "pk": "1",
            "visible": True
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.textblock",
            "pk": "1",
            "visible": True
        }]

        output = helpers.render_stream(stream)
        assert output == (
            '<h1>Example header</h1>\n'
            '<ul class="advantages">\n'
            '  <li>\n'
            '    <h4>Comfort Redefined</h4>\n'
            '    <p>Ergonomic design for fatigue-free hours of work.</p>\n'
            '  </li>\n'
            '  <li>\n'
            '    <h4>Precision in Action</h4>\n'
            '    <p>Navigate tasks with precise tracking and responsive controls.</p>\n'
            '  </li>\n'
            '  <li>\n'
            '    <h4>Unleash Wireless Freedom</h4>\n'
            '    <p>Experience unrestricted movement with our wireless technology.</p>\n'
            '  </li>\n'
            '</ul>\n'
            '<div><p>Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p></div>'
        )

    def test_skip(self):
        HeaderBlock.objects.create(
            pk=1,
            text="Example header"
        )

        TextBlock.objects.create(
            pk=1,
            text="Lorem ipsum dolor sit amet, consectetur adipisicing elit."
        )

        AdvantagesBlock.objects.create(
            pk=1,
        )

        Advantage.objects.create(
            pk=1,
            title="Comfort Redefined",
            description="Ergonomic design for fatigue-free hours of work."
        )
        Advantage.objects.create(
            pk=2,
            title="Precision in Action",
            description="Navigate tasks with precise tracking and responsive controls."
        )
        # Advantage.objects.create(
        #     pk=3,
        #     title="Unleash Wireless Freedom",
        #     description="Experience unrestricted movement with our wireless technology."
        # )

        stream = [{
            "uuid": str(uuid4()),
            "model": "blocks.headerblock",
            "pk": "1",
            "visible": True
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.advantagesblock",
            "pk": "1",
            "visible": True
        }, {
            "uuid": str(uuid4()),
            "model": "blocks.textblock",
            "pk": "1",
            "visible": True
        }]

        output = helpers.render_stream(stream)
        assert output == (
            '<h1>Example header</h1>\n'
            '<div><p>Lorem ipsum dolor sit amet, consectetur adipisicing elit.</p></div>'
        )
