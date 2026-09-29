import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import ComicRecord, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

settings = get_settings()
router = APIRouter()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def get_record_path(comic_id: str) -> Path:
    return settings.generated_dir / f"{comic_id}.json"


def save_record(record: ComicRecord) -> None:
    get_record_path(record.comic_id).write_text(
        record.model_dump_json(indent=2),
        encoding="utf-8",
    )


def load_record(comic_id: str) -> ComicRecord:
    if not comic_id.isalnum() or len(comic_id) > 32:
        raise HTTPException(status_code=404, detail="Comic not found")

    path = get_record_path(comic_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Comic not found")

    try:
        return ComicRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Stored comic is invalid") from exc


def generate_complete_comic(request_data: PromptRequest) -> ComicRecord:
    comic_id = uuid.uuid4().hex[:12]

    outline = generate_outline(
        request_data.story_prompt,
        request_data.character_name,
        request_data.setting,
        request_data.tone,
        request_data.art_style,
    )

    story = generate_story(
        outline,
        request_data.character_name,
        request_data.tone,
    )

    image_urls = [
        generate_image(
            panel.image_prompt,
            panel.panel_number,
            comic_id,
        )
        for panel in outline
    ]

    panels = build_comic_layout(outline, story, image_urls)

    record = ComicRecord(
        comic_id=comic_id,
        request=request_data,
        panels=panels,
        created_at=datetime.now(timezone.utc).isoformat(),
        pdf_url=f"/export/{comic_id}",
    )
    save_record(record)
    return record


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        comic = generate_complete_comic(data)
        return templates.TemplateResponse(
            "comic_preview.html",
            {"request": request, "comic": comic},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):
    comic = generate_complete_comic(data)
    return {
        "success": True,
        "comic_id": comic.comic_id,
        "layout": [panel.model_dump() for panel in comic.panels],
        "pdf_url": comic.pdf_url,
        "preview_url": f"/comic/{comic.comic_id}",
    }


@router.get("/comic/{comic_id}", response_class=HTMLResponse)
async def comic_preview(request: Request, comic_id: str):
    comic = load_record(comic_id)
    return templates.TemplateResponse(
        "comic_preview.html",
        {"request": request, "comic": comic},
    )


@router.get("/export/{comic_id}")
async def export_comic(comic_id: str):
    comic = load_record(comic_id)
    pdf_path = save_pdf(comic.panels, comic_id)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"comiccraft-{comic_id}.pdf",
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    comic_id: str | None = None,
):
    return templates.TemplateResponse(
        "export_success.html",
        {"request": request, "comic_id": comic_id},
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "image_provider": settings.image_provider,
    }
