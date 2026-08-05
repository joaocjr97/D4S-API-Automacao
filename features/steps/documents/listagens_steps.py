"""Steps de listagens de documentos / pins / webhooks."""

from __future__ import annotations

from behave import then, when

from recursos.utils.assertions import assert_equals, assert_not_empty
from recursos.utils.config import Config


def _require(value: str, name: str) -> str:
    if not value:
        raise AssertionError(
            f"{name} não configurado no .env. "
            "Preencha a variável antes de executar este cenário."
        )
    return value


@when("eu consulto todos os documentos da conta")
def listar_todos_documentos(context) -> None:  # noqa: ANN001
    context.response = context.documents_service.list_all()
    context.response_json = context.response.json()


@when("eu consulto o documento específico configurado")
def listar_documento_especifico(context) -> None:  # noqa: ANN001
    document_uuid = _require(Config.LIST_ESPECIFIC_DOCUMENT, "LIST_ESPECIFIC_DOCUMENT")
    context.response = context.documents_service.get_by_id(document_uuid)
    context.response_json = context.response.json()


@when("eu consulto os documentos pela fase configurada")
def listar_documentos_por_fase(context) -> None:  # noqa: ANN001
    context.response = context.documents_service.list_by_phase(Config.DOCUMENTS_PHASE)
    context.response_json = context.response.json()


@when("eu consulto os documentos do cofre configurado")
def listar_documentos_do_cofre(context) -> None:  # noqa: ANN001
    safe_uuid = _require(Config.UUID_SAFE, "UUID_SAFE")
    context.response = context.documents_service.list_by_safe(safe_uuid)
    context.response_json = context.response.json()


@when("eu consulto os webhooks do documento configurado")
def listar_webhooks(context) -> None:  # noqa: ANN001
    document_uuid = _require(Config.UUID_WEBHOOK_DOCUMENT, "UUID_WEBHOOK_DOCUMENT")
    context.response = context.documents_service.list_webhooks(document_uuid)
    context.response_json = context.response.json()


@when("eu consulto os pins do documento configurado")
def listar_pins(context) -> None:  # noqa: ANN001
    document_uuid = _require(Config.UUID_PINS, "UUID_PINS")
    context.response = context.documents_service.list_pins(document_uuid)
    context.response_json = context.response.json()


@then("o primeiro pin deve refletir os dados esperados do ambiente")
def validar_primeiro_pin(context) -> None:  # noqa: ANN001
    payload = context.response_json or context.response.json()
    assert_not_empty(payload, message="JSON de pins")
    pins = payload.get("pins") if isinstance(payload, dict) else None
    assert_not_empty(pins, message="lista pins")

    first_pin = pins[0]
    expected_email = _require(Config.EXPECTED_PIN_EMAIL, "EXPECTED_PIN_EMAIL")
    assert_equals(first_pin.get("email"), expected_email, message="pin.email")
    assert_equals(
        int(first_pin.get("position_x")),
        Config.EXPECTED_PIN_POSITION_X,
        message="pin.position_x",
    )
    assert_equals(
        str(first_pin.get("page_height")),
        Config.EXPECTED_PIN_PAGE_HEIGHT,
        message="pin.page_height",
    )
