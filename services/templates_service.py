"""Service de templates (Word / HTML) da API D4Sign."""

from __future__ import annotations

from typing import Any

from services.base_client import ApiResponse, BaseClient


class TemplatesService:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def create_from_word(
        self,
        safe_uuid: str,
        *,
        template_id: str,
        name_document: str,
        variables: dict[str, Any],
    ) -> ApiResponse:
        """POST /documents/{safe}/makedocumentbytemplateword."""
        body = {
            "name_document": name_document,
            "templates": {template_id: variables},
        }
        return self._client.post(
            f"/documents/{safe_uuid}/makedocumentbytemplateword",
            json_body=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def create_from_html(
        self,
        safe_uuid: str,
        *,
        template_id: str,
        name_document: str,
        variables: dict[str, Any],
    ) -> ApiResponse:
        """POST /documents/{safe}/makedocumentbytemplate."""
        body = {
            "name_document": name_document,
            "templates": {template_id: variables},
        }
        return self._client.post(
            f"/documents/{safe_uuid}/makedocumentbytemplate",
            json_body=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
