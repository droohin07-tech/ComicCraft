from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import (
    PromptRequest,
    ComicOutline,
    ComicStory,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

_client = None


def get_client():
    global _client

    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing from your .env file."
            )

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

    return _client


# ============================================================
# HELPERS
# ============================================================

def _model_dump(value: Any) -> Any:
    """
    Convert Pydantic objects into normal Python dictionaries.
    """
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return value

    return value


def _extract_json(response) -> Any:
    """
    Extract JSON from a Gemini response.

    Gemini can return:
        - a Python dictionary
        - a JSON string
        - fenced JSON
        - response.parsed
        - response.text
    """

    # --------------------------------------------------------
    # 1. Structured parsed response
    # --------------------------------------------------------

    parsed = getattr(response, "parsed", None)

    if parsed is not None:
        return _model_dump(parsed)

    # --------------------------------------------------------
    # 2. Raw response text
    # --------------------------------------------------------

    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # Remove markdown JSON fences if Gemini adds them
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON.\n\n"
            f"Raw response:\n{text}"
        ) from exc


def _extract_panels(data: Any) -> list:
    """
    Normalize all likely Gemini response structures into:

        [
            {...},
            {...},
            ...
        ]

    Accepted formats:

        {"panels": [...]}

        {"outline": {"panels": [...]}}

        {"story": {"panels": [...]}}

        [{"panel_number": 1, ...}, ...]
    """

    data = _model_dump(data)

    # --------------------------------------------------------
    # Direct list
    # --------------------------------------------------------

    if isinstance(data, list):
        return data

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(data, dict):

        # Normal expected format
        panels = data.get("panels")

        if isinstance(panels, list):
            return panels

        # Sometimes nested under "outline"
        outline = data.get("outline")

        if isinstance(outline, dict):
            panels = outline.get("panels")

            if isinstance(panels, list):
                return panels

        # Sometimes nested under "story"
        story = data.get("story")

        if isinstance(story, dict):
            panels = story.get("panels")

            if isinstance(panels, list):
                return panels

        # Sometimes Gemini wraps the actual result
        result = data.get("result")

        if isinstance(result, dict):
            panels = result.get("panels")

            if isinstance(panels, list):
                return panels

    raise RuntimeError(
        "Gemini outline did not contain a panel list.\n\n"
        f"Received:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
    )


# ============================================================
# GENERIC GEMINI JSON GENERATOR
# ============================================================

def _generate_json(
    prompt: str,
    schema,
):
    client = get_client()

    response = client.models.generate_content(
        model=settings.gemini_text_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    return _extract_json(response)


# ============================================================
# GENERATE 5-PANEL OUTLINE
# ============================================================

def generate_outline(
    prompt_data: PromptRequest,
) -> ComicOutline:

    prompt = f"""
You are a professional comic book story planner.

Create a complete comic story outline consisting of EXACTLY 5 panels.

USER STORY:
{prompt_data.story_prompt}

MAIN CHARACTER:
{prompt_data.character_name}

SETTING:
{prompt_data.setting}

TONE:
{prompt_data.tone}

ART STYLE:
{prompt_data.art_style}

Requirements:

1. Create EXACTLY 5 panels.
2. Each panel must advance the story.
3. Keep the main character consistent.
4. Make the visual descriptions detailed enough for an image-generation model.
5. Every image prompt must describe the actual scene to draw.
6. Do not put dialogue inside image prompts.
7. Do not include speech bubbles.
8. Do not include captions inside generated images.
9. Do not include watermarks.
10. Make the five panels form one coherent beginning, middle, and ending.

Return JSON matching the requested schema.
""".strip()

    raw_data = _generate_json(
        prompt,
        ComicOutline,
    )

    # --------------------------------------------------------
    # Normalize Gemini's response
    # --------------------------------------------------------

    panels = _extract_panels(raw_data)

    if len(panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(panels)} panels. "
            "Exactly 5 panels are required."
        )

    # Make sure panel numbers exist
    normalized_panels = []

    for index, panel in enumerate(panels, start=1):

        if not isinstance(panel, dict):
            raise RuntimeError(
                f"Panel {index} is not a JSON object."
            )

        panel = dict(panel)

        panel["panel_number"] = index

        normalized_panels.append(panel)

    return ComicOutline(
        panels=normalized_panels
    )


# ============================================================
# GENERATE STORY / DIALOGUE
# ============================================================

def generate_story(
    prompt_data: PromptRequest,
    outline: ComicOutline,
) -> ComicStory:

    outline_data = _model_dump(outline)

    prompt = f"""
You are a professional comic book script writer.

Create narration, captions, and dialogue for the following
5-panel comic.

ORIGINAL STORY:
{prompt_data.story_prompt}

MAIN CHARACTER:
{prompt_data.character_name}

SETTING:
{prompt_data.setting}

TONE:
{prompt_data.tone}

ART STYLE:
{prompt_data.art_style}

COMIC OUTLINE:
{json.dumps(
    outline_data,
    indent=2,
    ensure_ascii=False
)}

Requirements:

1. Create EXACTLY 5 panels.
2. Keep panel numbers 1 through 5.
3. Match the provided outline exactly.
4. Write concise comic captions.
5. Write concise narration.
6. Write natural dialogue.
7. Do not put dialogue into image prompts.
8. Do not create additional panels.
9. Keep character names and story events consistent.
10. The ending should provide a satisfying conclusion.

Return JSON matching the requested schema.
""".strip()

    raw_data = _generate_json(
        prompt,
        ComicStory,
    )

    panels = _extract_panels(raw_data)

    if len(panels) != 5:
        raise RuntimeError(
            f"Gemini returned {len(panels)} story panels. "
            "Exactly 5 panels are required."
        )

    normalized_panels = []

    for index, panel in enumerate(panels, start=1):

        if not isinstance(panel, dict):
            raise RuntimeError(
                f"Story panel {index} is not a JSON object."
            )

        panel = dict(panel)

        panel["panel_number"] = index

        normalized_panels.append(panel)

    return ComicStory(
        panels=normalized_panels
    )