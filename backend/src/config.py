"""Configuration centrale LEXIS-X5 backend."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Paramètres de l'application LEXIS-X5.

    Les valeurs peuvent être surchargées via variables d'environnement
    ou fichier ``.env`` à la racine du backend.
    """

    app_name: str = "LEXIS-X5"
    app_version: str = "0.1.0"
    debug: bool = False

    # Upload
    max_file_size_mb: int = 50
    allowed_content_types: list[str] = ["application/pdf"]

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
    ]

    model_config = {"env_prefix": "LEXIS_", "env_file": ".env"}

    @property
    def max_file_size_bytes(self) -> int:
        """Taille maximale de fichier en octets."""
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
