"""Steps de signatários e envio para assinatura."""

from __future__ import annotations

from behave import when

from recursos.utils.assertions import assert_equals, assert_not_empty, assert_status
from recursos.utils.config import Config


def _require_document(context) -> str:  # noqa: ANN001
    if not context.document_uuid:
        raise AssertionError("document_uuid ausente — faça o upload antes")
    return context.document_uuid


@when("eu adiciono um signatário por e-mail ao documento criado")
def adicionar_signatario_email(context) -> None:  # noqa: ANN001
    email = Config.EMAIL_TESTE or context.data_factory.email()
    context.signer_email = email
    signer = context.data_factory.signer_by_email(email).to_dict()
    response = context.signers_service.create_list(
        _require_document(context),
        [signer],
    )
    assert_status(response, 200)
    payload = response.json()
    message = payload.get("message")
    assert_not_empty(message, message="message de signatários")
    first = message[0] if isinstance(message, list) else message
    assert_equals(first.get("email"), email, message="email do signatário")
    context.key_signer = first.get("key_signer")
    context.response = response
    context.response_json = payload


@when("eu adiciono um signatário por WhatsApp ao documento criado")
def adicionar_signatario_whatsapp(context) -> None:  # noqa: ANN001
    whatsapp = Config.WHATSAPP_TESTE or context.data_factory.phone_br()
    context.signer_whatsapp = whatsapp
    signer = context.data_factory.signer_by_whatsapp(whatsapp).to_dict()
    response = context.signers_service.create_list(
        _require_document(context),
        [signer],
    )
    assert_status(response, 200)
    payload = response.json()
    first = payload["message"][0]
    # A API devolve o WhatsApp no campo email
    assert_equals(first.get("email"), whatsapp, message="whatsapp do signatário")
    context.key_signer = first.get("key_signer")
    context.response = response
    context.response_json = payload


@when("eu envio o documento para assinatura")
def enviar_para_assinatura(context) -> None:  # noqa: ANN001
    payload = context.data_factory.send_to_signer_payload()
    response = context.documents_service.send_to_signer(
        _require_document(context),
        payload,
    )
    context.response = response
    context.response_json = response.json()


@when("eu altero o e-mail do signatário cadastrado")
def alterar_email_signatario(context) -> None:  # noqa: ANN001
    if not context.key_signer:
        raise AssertionError("key_signer ausente")
    email_before = context.signer_email or Config.EMAIL_TESTE
    email_after = Config.EMAIL_ALTERADO
    context.signer_email_alterado = email_after
    response = context.signers_service.change_email(
        _require_document(context),
        email_before=email_before,
        email_after=email_after,
        key_signer=context.key_signer,
    )
    context.response = response
    context.response_json = response.json()


@when("eu removo o signatário alterado do documento")
def remover_signatario(context) -> None:  # noqa: ANN001
    if not context.key_signer:
        raise AssertionError("key_signer ausente")
    email = getattr(context, "signer_email_alterado", None) or Config.EMAIL_ALTERADO
    response = context.signers_service.remove(
        _require_document(context),
        email_signer=email,
        key_signer=context.key_signer,
    )
    context.response = response
    context.response_json = response.json()
