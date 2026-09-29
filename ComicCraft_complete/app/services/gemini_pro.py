import json

from app.config import get_settings
from app.models import ComicStory, PanelOutline


def get_client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in .env. "
            "Add a Gemini API key before generating an AI comic."
        )
    from google import genai
    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(
    outline: list[PanelOutline],
    character_name: str,
    tone: str,
) -> ComicStory:
    settings = get_settings()

    outline_text = "\n\n".join(
        (
            f"Panel {panel.panel_number}: {panel.title}\n"
            f"Scene: {panel.scene_description}"
        )
        for panel in outline
    )

    prompt = f"""
Turn this comic outline into a polished short comic script.

Character: {character_name}
Tone: {tone}

Outline:
{outline_text}

Return a JSON object with a `panels` array containing exactly
{settings.panel_count} items.

Every panel must contain:
panel_number, title, scene_description, caption, narration.

Requirements:
- Preserve the outline's panel order.
- Keep continuity between panels.
- Captions should be short.
- Narration should be concise and readable.
- Keep the story family-friendly.
"""

    response = get_client().models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=__import__("google.genai", fromlist=["types"]).types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicStory,
            temperature=0.85,
        ),
    )

    parsed = getattr(response, "parsed", None)

    if parsed is not None:
        story = ComicStory.model_validate(parsed)
    else:
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty script response.")
        story = ComicStory.model_validate(json.loads(text))

    if len(story.panels) != settings.panel_count:
        raise ValueError(
            f"Expected {settings.panel_count} story panels, "
            f"got {len(story.panels)}."
        )

    for index, panel in enumerate(story.panels, start=1):
        panel.panel_number = index

    return story
