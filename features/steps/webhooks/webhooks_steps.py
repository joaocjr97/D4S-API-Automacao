"""Steps de webhooks."""

from __future__ import annotations

from behave import when

from recursos.utils.config import Config


@when("eu adiciono um webhook ao documento configurado")
def adicionar_webhook(context) -> None:  # noqa: ANN001
    document_uuid = Config.UUID_DOC_WEBHOOK
    if not document_uuid:
        raise AssertionError("UUID_DOC_WEBHOOK não configurado no .env")

    response = context.webhooks_service.add(document_uuid, Config.URL_WEBHOOK)
    context.response = response
    context.response_json = response.json()
