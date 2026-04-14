"""Endpoint d'upload et parsing de documents PDF SST.

Couches 1 (INGEST) et 2 (PARSE) du pipeline LEXIS-X5.
Parsing 100% local via opendataloader-pdf, CPU only (Loi 25 Québec).
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, UploadFile, status
from opendataloader_pdf import convert as odl_convert
from pydantic import BaseModel

from src.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["upload"])


# ---------------------------------------------------------------------------
# Modèles de réponse
# ---------------------------------------------------------------------------


class UploadResponse(BaseModel):
    """Réponse structurée après upload et parsing d'un PDF SST."""

    filename: str
    pages: int
    tables_count: int
    elements_count: int
    markdown: str
    json_data: dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers parsing
# ---------------------------------------------------------------------------


def _count_tables_markdown(text: str) -> int:
    """Compte les blocs de tableaux dans du contenu Markdown."""
    count = 0
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("|"):
            if not in_table:
                count += 1
                in_table = True
        else:
            in_table = False
    return count


def _count_elements_markdown(text: str) -> int:
    """Compte les éléments structurels (lignes non vides) dans du Markdown."""
    return sum(1 for line in text.splitlines() if line.strip())


def _count_pages_markdown(text: str) -> int:
    """Estime le nombre de pages à partir des séparateurs opendataloader-pdf."""
    separators = len(re.findall(r"---\s*Page\s+\d+", text, re.IGNORECASE))
    return separators if separators > 0 else 1


def _extract_metadata_json(data: dict[str, Any]) -> tuple[int, int, int]:
    """Extrait pages, éléments et tableaux depuis la sortie JSON."""
    pages = len(data.get("pages", []))
    elements = 0
    tables = 0
    for page in data.get("pages", []):
        items = page.get("items", [])
        elements += len(items)
        tables += sum(1 for item in items if item.get("type") == "table")
    return max(pages, 1), elements, tables


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK)
async def upload_pdf(file: UploadFile) -> UploadResponse:
    """Upload et parse un document PDF SST.

    Accepte un fichier PDF (max 50 MB), le parse en Markdown et JSON
    via opendataloader-pdf en mode local, et retourne le résultat structuré.

    Args:
        file: Fichier PDF uploadé.

    Returns:
        Résultat structuré avec contenu Markdown, données JSON et métadonnées.

    Raises:
        HTTPException 400: Si le fichier n'est pas un PDF.
        HTTPException 413: Si le fichier dépasse la taille maximale.
        HTTPException 500: Si le parsing échoue.
    """
    # Validation Content-Type
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté : {file.content_type}. Seuls les PDFs sont acceptés.",
        )

    # Lecture du contenu et validation taille
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux : {len(content) / 1024 / 1024:.1f} MB (max {settings.max_file_size_mb} MB).",
        )

    filename = file.filename or "document.pdf"

    logger.info(
        "lexis.upload.debut",
        filename=filename,
        taille_mb=round(len(content) / 1024 / 1024, 2),
    )

    tmp_dir = tempfile.mkdtemp(prefix="lexis_upload_")
    try:
        # Écrire le PDF uploadé dans le répertoire temporaire
        pdf_path = Path(tmp_dir) / filename
        pdf_path.write_bytes(content)

        # Parse Markdown
        md_out_dir = tempfile.mkdtemp(prefix="lexis_md_", dir=tmp_dir)
        odl_convert(
            input_path=str(pdf_path),
            output_dir=md_out_dir,
            format="markdown",
            quiet=True,
        )

        md_files = list(Path(md_out_dir).glob("*.md"))
        if not md_files:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Le parsing Markdown n'a produit aucun résultat.",
            )
        markdown_content = md_files[0].read_text(encoding="utf-8")

        # Parse JSON
        json_out_dir = tempfile.mkdtemp(prefix="lexis_json_", dir=tmp_dir)
        odl_convert(
            input_path=str(pdf_path),
            output_dir=json_out_dir,
            format="json",
            quiet=True,
        )

        json_files = list(Path(json_out_dir).glob("*.json"))
        if not json_files:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Le parsing JSON n'a produit aucun résultat.",
            )
        json_data: dict[str, Any] = json.loads(
            json_files[0].read_text(encoding="utf-8")
        )

        # Métadonnées — priorité au JSON (plus précis), fallback Markdown
        pages_json, elements_json, tables_json = _extract_metadata_json(json_data)
        pages = pages_json
        elements_count = elements_json if elements_json > 0 else _count_elements_markdown(markdown_content)
        tables_count = tables_json if tables_json > 0 else _count_tables_markdown(markdown_content)

        logger.info(
            "lexis.upload.termine",
            filename=filename,
            pages=pages,
            elements=elements_count,
            tables=tables_count,
        )

        return UploadResponse(
            filename=filename,
            pages=pages,
            tables_count=tables_count,
            elements_count=elements_count,
            markdown=markdown_content,
            json_data=json_data,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("lexis.upload.erreur", filename=filename, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing du PDF : {exc}",
        ) from exc
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
