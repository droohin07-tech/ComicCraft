from __future__ import annotations

from typing import Any

from app.schemas import PromptRequest
from app.services.gemini_service import (
    generate_outline,
    generate_story,
)
from app.services.image_service import generate_image
from app.services.pdf_service import save_pdf


def _dump(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()

    return value


async def generate_comic(
    prompt_data: PromptRequest,
):

    # ========================================================
    # STEP 1: GENERATE OUTLINE
    # ========================================================

    outline = generate_outline(prompt_data)

    outline_data = _dump(outline)

    if isinstance(outline_data, dict):
        outline_panels = outline_data.get("panels", [])
    else:
        outline_panels = outline_data

    if not isinstance(outline_panels, list):
        raise RuntimeError(
            "Comic outline does not contain a valid panel list."
        )

    if len(outline_panels) != 5:
        raise RuntimeError(
            f"Expected 5 outline panels, "
            f"received {len(outline_panels)}."
        )

    # ========================================================
    # STEP 2: GENERATE STORY
    # ========================================================

    story = generate_story(
        prompt_data,
        outline,
    )

    story_data = _dump(story)

    if isinstance(story_data, dict):
        story_panels = story_data.get("panels", [])
    else:
        story_panels = story_data

    if not isinstance(story_panels, list):
        raise RuntimeError(
            "Comic story does not contain a valid panel list."
        )

    if len(story_panels) != 5:
        raise RuntimeError(
            f"Expected 5 story panels, "
            f"received {len(story_panels)}."
        )

    # ========================================================
    # STEP 3: GENERATE IMAGES
    # ========================================================

    comic_panels = []

    for index in range(5):

        outline_panel = outline_panels[index]
        story_panel = story_panels[index]

        image_prompt = outline_panel.get(
            "image_prompt",
            ""
        )

        if not image_prompt:
            image_prompt = outline_panel.get(
                "scene_description",
                ""
            )

        image_url = generate_image(
            image_prompt
        )

        comic_panels.append(
            {
                "panel_number": index + 1,
                "title": outline_panel.get(
                    "title",
                    f"Panel {index + 1}"
                ),
                "scene_description": outline_panel.get(
                    "scene_description",
                    ""
                ),
                "image_prompt": image_prompt,
                "image_url": image_url,
                "caption": story_panel.get(
                    "caption",
                    ""
                ),
                "narration": story_panel.get(
                    "narration",
                    ""
                ),
                "dialogue": story_panel.get(
                    "dialogue",
                    ""
                ),
            }
        )

    # ========================================================
    # STEP 4: GENERATE PDF
    # ========================================================

    pdf_path = save_pdf(
        title=prompt_data.story_prompt[:50],
        panels=comic_panels,
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "title": prompt_data.story_prompt,
        "panels": comic_panels,
        "pdf_path": pdf_path,
    }