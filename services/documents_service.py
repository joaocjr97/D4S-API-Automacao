"""Service de documentos da API D4Sign.

Cada método representa uma ação HTTP. Nenhuma lógica de assert aqui.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from services.base_client import ApiResponse, BaseClient


class DocumentsService:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def list_all(self) -> ApiResponse:
        """GET /documents — lista todos os documentos da conta."""
        return self._client.get("/documents")

    def get_by_id(self, document_uuid: str) -> ApiResponse:
        """GET /documents/{uuid} — documento específico."""
        return self._client.get(f"/documents/{document_uuid}")

    def list_by_phase(self, phase: int | str = 3) -> ApiResponse:
        """GET /documents/{phase}/status — documentos por fase."""
        return self._client.get(f"/documents/{phase}/status")

    def list_by_safe(self, safe_uuid: str) -> ApiResponse:
        """GET /documents/{safe_uuid}/safe — documentos de um cofre."""
        return self._client.get(f"/documents/{safe_uuid}/safe")

    def list_webhooks(self, document_uuid: str) -> ApiResponse:
        """GET /documents/{uuid}/webhooks."""
        return self._client.get(f"/documents/{document_uuid}/webhooks")

    def list_pins(self, document_uuid: str) -> ApiResponse:
        """GET /documents/{uuid}/listpins."""
        return self._client.get(f"/documents/{document_uuid}/listpins")

    def upload_pdf(self, safe_uuid: str, file_path: str | Path) -> ApiResponse:
        """POST /documents/{safe}/upload — upload multipart de PDF."""
        path = Path(file_path)
        with path.open("rb") as file_obj:
            files = {"file": (path.name, file_obj, "application/pdf")}
            return self._client.post(
                f"/documents/{safe_uuid}/upload",
                files=files,
                headers={"Accept": "application/json"},
            )

    def upload_binary(
        self,
        safe_uuid: str,
        *,
        base64_content: str,
        mime_type: str = "application/pdf",
        name: str | None = None,
    ) -> ApiResponse:
        body: dict[str, Any] = {
            "base64_binary_file": base64_content,
            "mime_type": mime_type,
        }
        if name:
            body["name"] = name
        return self._client.post(
            f"/documents/{safe_uuid}/uploadbinary",
            json_body=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def upload_hash(
        self,
        safe_uuid: str,
        *,
        sha256: str,
        sha512: str,
        name: str | None = None,
    ) -> ApiResponse:
        body: dict[str, Any] = {"sha256": sha256, "sha512": sha512}
        if name:
            body["name"] = name
        return self._client.post(
            f"/documents/{safe_uuid}/uploadhash",
            json_body=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def upload_slave(self, document_uuid: str, file_path: str | Path) -> ApiResponse:
        """POST /documents/{uuid}/uploadslave — anexa PDF ao documento."""
        path = Path(file_path)
        with path.open("rb") as file_obj:
            files = {"file": (path.name, file_obj, "application/pdf")}
            return self._client.post(
                f"/documents/{document_uuid}/uploadslave",
                files=files,
                headers={"Accept": "application/json"},
            )

    def send_to_signer(
        self,
        document_uuid: str,
        payload: dict[str, Any] | None = None,
    ) -> ApiResponse:
        body = payload or {"skip_email": 1, "workflow": 0}
        return self._client.post(
            f"/documents/{document_uuid}/sendtosigner",
            json_body=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
