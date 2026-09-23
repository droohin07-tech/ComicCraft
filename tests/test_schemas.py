from app.schemas import (
    ComicOutline,
    PanelOutline,
    PromptRequest,
)


def test_prompt_request():

    data = PromptRequest(
        story_prompt=(
            "A fox finds a hidden door."
        ),

        character_name="Luna",

        setting="Forest",

        tone="Funny",

        art_style="Comic book",
    )

    assert data.character_name == "Luna"


def test_outline_requires_five_panels():

    panels = [

        PanelOutline(
            panel_number=i,
            title=f"Panel {i}",
            scene_description="Scene",
            image_prompt="Comic scene",
        )

        for i in range(1, 6)
    ]

    outline = ComicOutline(
        panels=panels
    )

    assert len(outline.panels) == 5