"""Point d'entrée LEXIS-X5 backend — FastAPI application."""

from __future__ import annotations

import os
import shutil

import structlog

# Garantir que java est accessible dans le PATH du processus.
# Sur Windows, le PATH hérité par le sous-processus uvicorn peut ne pas
# inclure JAVA_HOME/bin, ce qui provoque [WinError 2] dans opendataloader-pdf.
if not shutil.which("java"):
    java_home = os.environ.get("JAVA_HOME", "")
    if java_home:
        java_bin = os.path.join(java_home, "bin")
        os.environ["PATH"] = java_bin + os.pathsep + os.environ.get("PATH", "")
    else:
        # Emplacement par défaut Adoptium sur Windows
        _default = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot\bin"
        if os.path.isfile(os.path.join(_default, "java.exe")):
            os.environ["PATH"] = _default + os.pathsep + os.environ.get("PATH", "")
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
