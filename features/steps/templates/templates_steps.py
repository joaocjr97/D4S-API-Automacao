"""Steps de templates Word/HTML."""

from __future__ import annotations

from behave import when

from recursos.utils.assertions import assert_status, assert_success_upload
from recursos.utils.config import Config


def _require_safe() -> str:
    if not Config.UUID_SAFE:
        raise AssertionError("UUID_SAFE não configurado no .env")
    return Config.UUID_SAFE


@when("eu gero um documento via template Word no cofre configurado")
def gerar_template_word(context) -> None:  # noqa: ANN001
    if not Config.TEMPLATE_ID_WORD:
        raise AssertionError("TEMPLATE_ID_WORD não configurado no .env")

    variables = context.data_factory.word_template_vars()
    response = context.templates_service.create_from_word(
        _require_safe(),
        template_id=Config.TEMPLATE_ID_WORD,
        name_document=Config.TEMPLATE_NAME_WORD,
        variables=variables,
    )
    context.response = response
    if response.ok:
        context.document_uuid = assert_success_upload(response)
    context.response_json = response.json()


@when("eu gero um documento via template HTML no cofre configurado")
def gerar_template_html(context) -> None:  # noqa: ANN001
    if not Config.TEMPLATE_ID_HTML:
        raise AssertionError("TEMPLATE_ID_HTML não configurado no .env")

    variables = context.data_factory.html_template_vars()
    response = context.templates_service.create_from_html(
        _require_safe(),
        template_id=Config.TEMPLATE_ID_HTML,
        name_document=Config.TEMPLATE_NAME_HTML,
        variables=variables,
    )
    assert_status(response, 200)
    context.response = response
    context.response_json = response.json()
    uuid_value = response.json().get("uuid")
    if uuid_value:
        context.document_uuid = uuid_value
