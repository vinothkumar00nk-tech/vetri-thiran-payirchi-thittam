import json

from app.config import get_settings
from app.models import PanelOutline


def get_client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in .env. "
            "Add a Gemini API key before generating an AI comic."
        )
    from google import genai
    return genai.Client(api_key=settings.gemini_api_key)


def _parse_outline(response) -> list[PanelOutline]:
    parsed = getattr(response, "parsed", None)

    if parsed is not None:
        if isinstance(parsed, list):
            return [PanelOutline.model_validate(item) for item in parsed]

        if isinstance(parsed, dict) and "panels" in parsed:
            return [
                PanelOutline.model_validate(item)
                for item in parsed["panels"]
            ]

        try:
            return [PanelOutline.model_validate(item) for item in parsed]
        except TypeError:
            pass

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty outline response.")

    data = json.loads(text)
    if isinstance(data, dict) and "panels" in data:
        data = data["panels"]

    return [PanelOutline.model_validate(item) for item in data]


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> list[PanelOutline]:
    settings = get_settings()

    prompt = f"""
Create exactly {settings.panel_count} comic panel outlines.

Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return JSON only as an array. Every item must contain:
panel_number, title, scene_description, image_prompt.

Requirements:
- Keep the character's appearance and story continuity consistent.
- Make the story flow clearly from panel 1 to panel {settings.panel_count}.
- Image prompts must describe visuals only.
- Do not put dialogue, readable text, logos, watermarks or speech bubbles in images.
- Keep the content family-friendly.
"""

    response = get_client().models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=__import__("google.genai", fromlist=["types"]).types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[PanelOutline],
            temperature=0.8,
        ),
    )

    panels = _parse_outline(response)

    if len(panels) != settings.panel_count:
        raise ValueError(
            f"Expected {settings.panel_count} panels, got {len(panels)}."
        )

    for index, panel in enumerate(panels, start=1):
        panel.panel_number = index

    return panels
