"""Service de pins (posições de assinatura) da API D4Sign."""

from __future__ import annotations

from typing import Any

from services.base_client import ApiResponse, BaseClient


class PinsService:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def add_pins(
        self,
        document_uuid: str,
        pins: list[dict[str, Any]],
    ) -> ApiResponse:
        """POST /documents/{uuid}/addpins."""
        return self._client.post(
            f"/documents/{document_uuid}/addpins",
            json_body={"pins": pins},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def add_pins_with_replicas(
        self,
        document_uuid: str,
        pin: dict[str, Any],
    ) -> ApiResponse:
        """POST /documents/{uuid}/addpinswithreplics — replica em todas as páginas."""
        return self._client.post(
            f"/documents/{document_uuid}/addpinswithreplics",
            json_body={"pins": pin},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def list_pins(self, document_uuid: str) -> ApiResponse:
        """GET /documents/{uuid}/listpins."""
        return self._client.get(f"/documents/{document_uuid}/listpins")
