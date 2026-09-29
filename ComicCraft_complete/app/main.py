from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.create_directories()
    yield


app = FastAPI(
    title="ComicCraft",
    description="AI-powered comic story, illustration and PDF generator.",
    version="2.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=str(settings.static_dir)),
    name="static",
)

app.include_router(router)
