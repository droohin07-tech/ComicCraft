from __future__ import annotations

import inspect
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.schemas import PromptRequest
from app.services.comic_service import generate_comic
from app.services.image_service import generate_image


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


async def run_comic_generation(prompt_data: PromptRequest):
    """
    Runs generate_comic() safely whether the implementation
    is synchronous or asynchronous.

    This prevents:
        TypeError: object dict can't be used in 'await' expression
    """

    result = generate_comic(prompt_data)

    if inspect.isawaitable(result):
        result = await result

    return result


@router.get("/")
async def home(request: Request):
    """
    Homepage.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ComicCraft",
        },
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    """
    Generate a complete comic from the HTML form.

    Flow:
        User input
        ↓
        PromptRequest
        ↓
        Gemini outline
        ↓
        Gemini story
        ↓
        Image generation
        ↓
        Comic layout
        ↓
        PDF export
        ↓
        Preview page
    """

    try:
        prompt_data = PromptRequest(
            story_prompt=story_prompt.strip(),
            character_name=character_name.strip(),
            setting=setting.strip(),
            tone=tone.strip(),
            art_style=art_style.strip(),
        )

        result = await run_comic_generation(prompt_data)

        if result is None:
            raise RuntimeError(
                "Comic generation returned no result."
            )

        # The comic service should return a dictionary.
        if not isinstance(result, dict):
            raise RuntimeError(
                f"Unexpected comic generation result type: "
                f"{type(result).__name__}"
            )

        # Support the expected result structure.
        layout = result.get("layout", result.get("panels", []))
        pdf_path = result.get("pdf_path", result.get("pdf_url", ""))

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": "Your Comic - ComicCraft",
                "layout": layout,
                "panels": layout,
                "pdf_path": pdf_path,
                "result": result,
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        print("\n" + "=" * 70)
        print("COMIC GENERATION ERROR")
        print("=" * 70)
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"Comic generation failed: {exc}",
        )


@router.post("/generate-comic/json")
async def generate_comic_json(prompt_data: PromptRequest):
    """
    JSON API version of comic generation.

    Example JSON:

    {
        "story_prompt": "A student discovers a mysterious robot.",
        "character_name": "Arun",
        "setting": "A futuristic college",
        "tone": "Funny and adventurous",
        "art_style": "Comic book"
    }
    """

    try:
        result = await run_comic_generation(prompt_data)

        if result is None:
            raise RuntimeError(
                "Comic generation returned no result."
            )

        if not isinstance(result, dict):
            raise RuntimeError(
                f"Unexpected comic generation result type: "
                f"{type(result).__name__}"
            )

        return JSONResponse(
            content=result
        )

    except HTTPException:
        raise

    except Exception as exc:
        print("\n" + "=" * 70)
        print("JSON COMIC GENERATION ERROR")
        print("=" * 70)
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"Comic generation failed: {exc}",
        )


@router.post("/test-image")
async def test_image(
    prompt: str = Form(...)
):
    """
    Test image generation independently.

    This is useful for checking Hugging Face image generation
    without spending another Gemini request.
    """

    try:
        image_url = generate_image(
            prompt=prompt.strip()
        )

        if inspect.isawaitable(image_url):
            image_url = await image_url

        return {
            "success": True,
            "image_url": image_url,
        }

    except Exception as exc:
        print("\n" + "=" * 70)
        print("IMAGE GENERATION ERROR")
        print("=" * 70)
        print(type(exc).__name__)
        print(str(exc))
        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {exc}",
        )


@router.get("/export-success")
async def export_success(
    request: Request,
    pdf_path: str = "",
):
    """
    PDF export confirmation page.
    """

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title": "Comic Exported - ComicCraft",
            "pdf_path": pdf_path,
        },
    )


@router.get("/health")
async def health():
    """
    Simple health check.
    """

    return {
        "status": "ok",
        "application": "ComicCraft",
    }