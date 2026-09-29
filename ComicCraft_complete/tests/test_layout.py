import pytest

from app.models import ComicStory, PanelOutline, PanelStory
from app.services.layout_builder import build_comic_layout


def test_layout_builder():
    outline = [
        PanelOutline(
            panel_number=1,
            title="One",
            scene_description="Scene one",
            image_prompt="Prompt one",
        ),
        PanelOutline(
            panel_number=2,
            title="Two",
            scene_description="Scene two",
            image_prompt="Prompt two",
        ),
    ]

    story = ComicStory(
        panels=[
            PanelStory(
                panel_number=1,
                title="One",
                scene_description="Scene one",
                caption="Cap 1",
                narration="Nar 1",
            ),
            PanelStory(
                panel_number=2,
                title="Two",
                scene_description="Scene two",
                caption="Cap 2",
                narration="Nar 2",
            ),
        ]
    )

    result = build_comic_layout(
        outline,
        story,
        ["/a.png", "/b.png"],
    )

    assert len(result) == 2
    assert result[0].image_url == "/a.png"
    assert result[1].narration == "Nar 2"


def test_layout_mismatch():
    with pytest.raises(ValueError):
        build_comic_layout(
            [],
            ComicStory(panels=[]),
            ["/a.png"],
        )
