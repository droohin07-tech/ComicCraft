from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse

from app.schemas import PromptRequest

from app.services.comic_service import (
    generate_comic,
)

from app.services.image_service import (
    generate_test_image,
)


router = APIRouter()


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return request.app.state.templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        data = generate_comic(
            payload
        )

        request.app.state.last_comic = data

        return (
            request.app.state.templates
            .TemplateResponse(
                "comic_preview.html",
                {
                    "request": request,
                    **data
                }
            )
        )

    except Exception as exc:

        return (
            request.app.state.templates
            .TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": str(exc)
                },
                status_code=500
            )
        )


@router.post(
    "/generate-comic/json"
)
async def generate_json(
    payload: PromptRequest
):

    try:

        return generate_comic(
            payload
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.post(
    "/test-image"
)
async def test_image(
    prompt: str = Form(...)
):

    try:

        image_url = generate_test_image(
            prompt
        )

        return {
            "image_url": image_url
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request
):

    comic = getattr(
        request.app.state,
        "last_comic",
        None
    )

    return (
        request.app.state.templates
        .TemplateResponse(
            "export_success.html",
            {
                "request": request,
                "pdf_url":
                    comic.get("pdf_url")
                    if comic
                    else None
            }
        )
    )


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "ComicCraft"
    }