from app.schemas import PromptRequest

from app.services.gemini_service import GeminiService
from app.services.image_service import ImageService
from app.services.pdf_service import save_pdf


def generate_comic(
    request: PromptRequest
) -> dict:

    gemini = GeminiService()
    image_service = ImageService()

    # STEP 1
    # Generate structured five-panel outline
    outline = gemini.generate_outline(
        request
    )

    # STEP 2
    # Generate narration/dialogue
    story = gemini.generate_story(
        request,
        outline
    )

    story_by_panel = {
        panel.panel_number: panel
        for panel in story.panels
    }

    panels = []

    # STEP 3
    # Generate images
    for outline_panel in outline.panels:

        story_panel = story_by_panel[
            outline_panel.panel_number
        ]

        image_url = image_service.generate_image(
            outline_panel.image_prompt,
            outline_panel.panel_number
        )

        panels.append({
            "panel_number":
                outline_panel.panel_number,

            "title":
                outline_panel.title,

            "scene_description":
                outline_panel.scene_description,

            "image_prompt":
                outline_panel.image_prompt,

            "image_url":
                image_url,

            "caption":
                story_panel.caption,

            "narration":
                story_panel.narration,

            "dialogue":
                story_panel.dialogue,
        })

    title = (
        f"{request.character_name}: "
        f"{request.story_prompt[:70]}"
    )

    # STEP 4
    # Generate PDF
    pdf_url = save_pdf(
        title,
        panels
    )

    return {
        "title": title,
        "panels": panels,
        "pdf_url": pdf_url,
    }