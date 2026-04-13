"""Point d'entrée LEXIS-X5 backend — FastAPI application."""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.upload import router as upload_router
from src.config import settings

logger = structlog.get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Document Intelligence Agentique pour la SST",
)

# CORS — dev local (tout port localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://localhost:\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Vérification de santé du backend."""
    return {"status": "ok", "service": settings.app_name}


@app.on_event("startup")
async def on_startup() -> None:
    """Initialisation au démarrage du serveur."""
    logger.info(
        "lexis.startup",
        app=settings.app_name,
        version=settings.app_version,
    )
