"""Service de cofres (safes) da API D4Sign."""

from __future__ import annotations

from services.base_client import ApiResponse, BaseClient


class SafesService:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list_all(self) -> ApiResponse:
        """GET /safes — lista todos os cofres da conta."""
        return self._client.get("/safes")
