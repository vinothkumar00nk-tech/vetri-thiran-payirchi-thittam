from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


def _font(size: int):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return ImageFont.load_default()


def generate_mock_image(prompt: str) -> Image.Image:
    settings = get_settings()
    width, height = settings.image_width, settings.image_height

    image = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(image)

    # Simple comic-like background.
    margin = 40
    draw.rounded_rectangle(
        (margin, margin, width - margin, height - margin),
        radius=28,
        outline=(25, 35, 55),
        width=6,
        fill=(255, 255, 255),
    )

    title_font = _font(max(28, width // 22))
    body_font = _font(max(18, width // 34))

    draw.text(
        (margin + 30, margin + 25),
        "ComicCraft • Demo Panel",
        font=title_font,
        fill=(20, 30, 50),
    )

    # A simple character + sun + ground illustration.
    cx, cy = width // 2, height // 2
    draw.ellipse(
        (cx - 80, cy - 170, cx + 80, cy - 10),
        outline=(20, 30, 50),
        width=7,
        fill=(230, 238, 248),
    )
    draw.ellipse(
        (cx - 28, cy - 110, cx - 10, cy - 92),
        fill=(20, 30, 50),
    )
    draw.ellipse(
        (cx + 10, cy - 110, cx + 28, cy - 92),
        fill=(20, 30, 50),
    )
    draw.arc(
        (cx - 32, cy - 78, cx + 32, cy - 32),
        start=10,
        end=170,
        fill=(20, 30, 50),
        width=5,
    )
    draw.line((cx, cy - 10, cx, cy + 125), fill=(20, 30, 50), width=8)
    draw.line((cx, cy + 35, cx - 70, cy + 90), fill=(20, 30, 50), width=8)
    draw.line((cx, cy + 35, cx + 70, cy + 90), fill=(20, 30, 50), width=8)
    draw.line((cx, cy + 125, cx - 55, cy + 200), fill=(20, 30, 50), width=8)
    draw.line((cx, cy + 125, cx + 55, cy + 200), fill=(20, 30, 50), width=8)

    text = "Demo mode. Set IMAGE_PROVIDER=hf for AI-generated images."
    lines = wrap(text, width=48)
    y = height - 170
    for line in lines:
        draw.text(
            (margin + 30, y),
            line,
            font=body_font,
            fill=(45, 55, 75),
        )
        y += body_font.size + 8

    # Keep the actual prompt available visually without pretending it is AI art.
    prompt_lines = wrap(prompt, width=58)[:5]
    y += 8
    draw.text((margin + 30, y), "Prompt:", font=body_font, fill=(20, 30, 50))
    y += body_font.size + 4
    for line in prompt_lines:
        draw.text((margin + 30, y), line, font=body_font, fill=(70, 80, 100))
        y += body_font.size + 4

    return image


def generate_huggingface_image(prompt: str) -> Image.Image:
    settings = get_settings()

    if not settings.hf_api_key:
        raise RuntimeError(
            "HF_API_KEY is missing in .env. "
            "Add a Hugging Face token or use IMAGE_PROVIDER=mock."
        )

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider="hf-inference",
        token=settings.hf_api_key,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.image_model,
    )

    if not isinstance(image, Image.Image):
        image = Image.open(image)

    return image.convert("RGB")


def generate_image(
    image_prompt: str,
    panel_number: int,
    comic_id: str,
) -> str:
    settings = get_settings()

    prompt = (
        f"{image_prompt}. "
        f"{settings.app_name} comic panel, panel {panel_number}, "
        "consistent character appearance, cinematic composition, "
        "clear focal subject, polished illustration, no text, "
        "no speech bubbles, no logos, no watermark."
    )

    provider = settings.image_provider.lower().strip()

    if provider == "mock":
        image = generate_mock_image(prompt)
    elif provider == "hf":
        image = generate_huggingface_image(prompt)
    else:
        raise ValueError(
            f"Unsupported IMAGE_PROVIDER='{settings.image_provider}'. "
            "Use 'mock' or 'hf'."
        )

    filename = f"{comic_id}_panel_{panel_number}.png"
    path = settings.panels_dir / filename
    image.save(path, format="PNG")

    return f"/static/panels/{filename}"
