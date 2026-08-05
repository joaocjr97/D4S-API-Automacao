"""Service de signatários da API D4Sign."""

from __future__ import annotations

from typing import Any

from services.base_client import ApiResponse, BaseClient


class SignersService:
    def __init__(self, client: BaseClient) -> None:
        self._client = client

    def create_list(
        self,
        document_uuid: str,
        signers: list[dict[str, Any]],
    ) -> ApiResponse:
        """POST /documents/{uuid}/createlist."""
        return self._client.post(
            f"/documents/{document_uuid}/createlist",
            json_body={"signers": signers},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def change_email(
        self,
        document_uuid: str,
        *,
        email_before: str,
        email_after: str,
        key_signer: str,
    ) -> ApiResponse:
        """POST /documents/{uuid}/changeemail."""
        return self._client.post(
            f"/documents/{document_uuid}/changeemail",
            json_body={
                "email-before": email_before,
                "email-after": email_after,
                "key-signer": key_signer,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def remove(
        self,
        document_uuid: str,
        *,
        email_signer: str,
        key_signer: str,
    ) -> ApiResponse:
        """POST /documents/{uuid}/removeemaillist."""
        return self._client.post(
            f"/documents/{document_uuid}/removeemaillist",
            json_body={
                "email-signer": email_signer,
                "key-signer": key_signer,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
