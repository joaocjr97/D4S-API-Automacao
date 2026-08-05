"""Steps comuns de validação de resposta HTTP."""

from __future__ import annotations

from behave import given, then

from recursos.utils.assertions import (
    assert_message,
    assert_not_empty,
    assert_response_time,
    assert_status,
)
from recursos.utils.config import Config


@given("que a API D4Sign está configurada")
def api_configurada(context) -> None:  # noqa: ANN001
    Config.require_api_credentials()
    assert context.client is not None, "BaseClient não inicializado"
    assert context.documents_service is not None, "DocumentsService não inicializado"
    assert context.safes_service is not None, "SafesService não inicializado"


@then("a resposta deve ter status {status:d}")
def resposta_status(context, status: int) -> None:  # noqa: ANN001
    assert_status(context.response, status)


@then("o corpo da resposta não deve estar vazio")
def corpo_nao_vazio(context) -> None:  # noqa: ANN001
    assert_not_empty(context.response.text, message="body da resposta")


@then("o tempo de resposta deve ser menor que {max_seconds:g} segundos")
def tempo_resposta(context, max_seconds: float) -> None:  # noqa: ANN001
    assert_response_time(context.response, max_seconds)


@then('a mensagem da resposta deve ser "{mensagem}"')
def mensagem_resposta(context, mensagem: str) -> None:  # noqa: ANN001
    assert_message(context.response, mensagem)


@then("o upload deve ter sido concluído com sucesso")
def upload_sucesso(context) -> None:  # noqa: ANN001
    from recursos.utils.assertions import assert_success_upload

    uuid_value = assert_success_upload(context.response)
    context.document_uuid = uuid_value

