from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routes import router


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI comic story and illustration generator."
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=settings.output_dir
    ),
    name="static"
)


app.state.templates = Jinja2Templates(
    directory=settings.templates_dir
)


app.include_router(router)


@app.on_event("startup")
async def startup():

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    settings.exports_dir.mkdir(
        parents=True,
        exist_ok=True
    )