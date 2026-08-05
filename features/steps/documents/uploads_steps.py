"""Steps de upload de documentos."""

from __future__ import annotations

from behave import when

from recursos.utils.assertions import assert_status, assert_success_upload
from recursos.utils.config import Config
from recursos.utils.helpers import (
    ensure_file_exists,
    file_sha256,
    file_sha512,
    file_to_base64,
)


def _require_safe() -> str:
    if not Config.UUID_SAFE:
        raise AssertionError("UUID_SAFE não configurado no .env")
    return Config.UUID_SAFE


def _store_document(context, response) -> None:  # noqa: ANN001
    context.response = response
    context.response_json = response.json()
    if response.ok:
        try:
            context.document_uuid = response.json().get("uuid") or context.document_uuid
        except Exception:  # noqa: BLE001
            pass


@when("eu faço upload de um PDF para o cofre configurado")
def upload_pdf(context) -> None:  # noqa: ANN001
    pdf = ensure_file_exists(Config.doc_testes_pdf())
    response = context.documents_service.upload_pdf(_require_safe(), pdf)
    assert_status(response, 200)
    context.document_uuid = assert_success_upload(response)
    _store_document(context, response)


@when("eu faço upload binário em base64 para o cofre configurado")
def upload_binario(context) -> None:  # noqa: ANN001
    pdf = ensure_file_exists(Config.doc_testes_pdf())
    name = context.data_factory.document_name("Documento Base64 API").name
    response = context.documents_service.upload_binary(
        _require_safe(),
        base64_content=file_to_base64(pdf),
        mime_type="application/pdf",
        name=name,
    )
    _store_document(context, response)


@when("eu faço upload por hash SHA256 e SHA512 para o cofre configurado")
def upload_hash(context) -> None:  # noqa: ANN001
    pdf = ensure_file_exists(Config.doc_testes_pdf())
    name = context.data_factory.document_name("Documento Hash API").name
    response = context.documents_service.upload_hash(
        _require_safe(),
        sha256=file_sha256(pdf),
        sha512=file_sha512(pdf),
        name=name,
    )
    _store_document(context, response)


@when("eu adiciono um anexo PDF ao documento criado")
def upload_anexo(context) -> None:  # noqa: ANN001
    if not context.document_uuid:
        raise AssertionError("document_uuid ausente — faça o upload antes")
    pdf = ensure_file_exists(Config.doc_testes_pdf())
    response = context.documents_service.upload_slave(context.document_uuid, pdf)
    _store_document(context, response)
