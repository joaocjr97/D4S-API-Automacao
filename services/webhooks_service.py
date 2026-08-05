"""Service de webhooks da API D4Sign."""

from __future__ import annotations

from services.base_client import ApiResponse, BaseClient


class WebhooksService:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def add(self, document_uuid: str, url: str) -> ApiResponse:
        """POST /documents/{uuid}/webhooks."""
        return self._client.post(
            f"/documents/{document_uuid}/webhooks",
            json_body={"url": url},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def list(self, document_uuid: str) -> ApiResponse:
        """GET /documents/{uuid}/webhooks."""
        return self._client.get(f"/documents/{document_uuid}/webhooks")
