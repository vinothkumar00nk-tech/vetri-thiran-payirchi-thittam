from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    story_prompt: str = Field(min_length=5, max_length=2000)
    character_name: str = Field(min_length=1, max_length=100)
    setting: str = Field(min_length=1, max_length=200)
    tone: str = Field(min_length=1, max_length=100)
    art_style: str = Field(min_length=1, max_length=100)

    @field_validator("*")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value cannot be blank.")
        return value


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class PanelStory(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str


class ComicStory(BaseModel):
    panels: List[PanelStory]


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    image_url: str
    image_prompt: str
    scene_description: str
    caption: str
    narration: str


class ComicRecord(BaseModel):
    comic_id: str
    request: PromptRequest
    panels: List[ComicPanel]
    created_at: str
    pdf_url: str | None = None
