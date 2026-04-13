"""Tests unitaires pour l'endpoint POST /api/v1/upload."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

_FAKE_MARKDOWN = "# Rapport SST\n\nContenu du rapport.\n\n| Danger | Niveau |\n| --- | --- |\n| Bruit | Élevé |"

_FAKE_JSON = {
    "pages": [
        {
            "items": [
                {"type": "paragraph", "content": "Contenu du rapport."},
                {"type": "table", "content": "| Danger | Niveau |"},
            ]
        },
        {
            "items": [
                {"type": "paragraph", "content": "Page 2."},
            ]
        },
    ]
}


def _mock_convert(input_path: str, output_dir: str, format: str, **kwargs: object) -> None:
    """Simule opendataloader-pdf convert() en écrivant le fichier de sortie."""
    stem = Path(input_path).stem
    if format == "markdown":
        output = Path(output_dir) / f"{stem}.md"
        output.write_text(_FAKE_MARKDOWN, encoding="utf-8")
    elif format == "json":
        output = Path(output_dir) / f"{stem}.json"
        output.write_text(json.dumps(_FAKE_JSON), encoding="utf-8")


class TestUploadEndpoint:
    """Tests de l'endpoint POST /api/v1/upload."""

    @patch("src.api.upload.odl_convert", side_effect=_mock_convert)
    def test_upload_pdf_ok(self, mock_convert: MagicMock) -> None:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("rapport.pdf", b"%PDF-1.4 fake content", "application/pdf")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "rapport.pdf"
        assert "markdown" in data
        assert "json_data" in data

    @patch("src.api.upload.odl_convert", side_effect=_mock_convert)
    def test_upload_retourne_metadata(self, mock_convert: MagicMock) -> None:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        data = response.json()
        assert data["pages"] == 2
        assert data["elements_count"] == 3
        assert data["tables_count"] == 1

    @patch("src.api.upload.odl_convert", side_effect=_mock_convert)
    def test_upload_contenu_markdown(self, mock_convert: MagicMock) -> None:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        data = response.json()
        assert "# Rapport SST" in data["markdown"]
        assert "Bruit" in data["markdown"]

    @patch("src.api.upload.odl_convert", side_effect=_mock_convert)
    def test_upload_contenu_json(self, mock_convert: MagicMock) -> None:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        data = response.json()
        assert "pages" in data["json_data"]
        assert len(data["json_data"]["pages"]) == 2

    def test_upload_rejette_non_pdf(self) -> None:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("doc.txt", b"Hello world", "text/plain")},
        )

        assert response.status_code == 400
        assert "non supporté" in response.json()["detail"]

    def test_upload_rejette_fichier_trop_gros(self) -> None:
        # Simuler un fichier de 51 MB
        big_content = b"x" * (51 * 1024 * 1024)

        response = client.post(
            "/api/v1/upload",
            files={"file": ("gros.pdf", big_content, "application/pdf")},
        )

        assert response.status_code == 413
        assert "trop volumineux" in response.json()["detail"]

    @patch("src.api.upload.odl_convert", side_effect=RuntimeError("Java not found"))
    def test_upload_erreur_parsing(self, mock_convert: MagicMock) -> None:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        assert response.status_code == 500
        assert "Erreur" in response.json()["detail"]


class TestHealthCheck:
    """Tests du endpoint health check."""

    def test_health_ok(self) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "LEXIS-X5"
