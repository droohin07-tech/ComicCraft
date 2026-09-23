from typing import List

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        min_length=5,
        max_length=2000
    )

    character_name: str = Field(
        min_length=1,
        max_length=80
    )

    setting: str = Field(
        min_length=1,
        max_length=120
    )

    tone: str = Field(
        min_length=1,
        max_length=60
    )

    art_style: str = Field(
        min_length=1,
        max_length=100
    )

    @field_validator("*")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class PanelOutline(BaseModel):
    panel_number: int = Field(
        ge=1,
        le=5
    )

    title: str = Field(
        min_length=1,
        max_length=120
    )

    scene_description: str = Field(
        min_length=1,
        max_length=1000
    )

    image_prompt: str = Field(
        min_length=1,
        max_length=1800
    )


class ComicOutline(BaseModel):
    panels: List[PanelOutline] = Field(
        min_length=5,
        max_length=5
    )


class PanelStory(BaseModel):
    panel_number: int = Field(
        ge=1,
        le=5
    )

    caption: str = Field(
        default="",
        max_length=500
    )

    narration: str = Field(
        default="",
        max_length=1200
    )

    dialogue: str = Field(
        default="",
        max_length=1200
    )


class ComicStory(BaseModel):
    panels: List[PanelStory] = Field(
        min_length=5,
        max_length=5
    )


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    image_url: str
    caption: str
    narration: str
    dialogue: str


class ComicResponse(BaseModel):
    title: str
    panels: List[ComicPanel]
    pdf_url: str