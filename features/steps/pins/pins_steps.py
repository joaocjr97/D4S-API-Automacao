"""Steps de pins."""

from __future__ import annotations

from behave import when

from recursos.utils.assertions import assert_status
from recursos.utils.config import Config


def _pin_dict(email: str, position_x: int, position_y: int, pin_type: int, document_uuid: str) -> dict:
    return {
        "document": document_uuid,
        "email": email,
        "page_width": Config.PAGE_WIDTH,
        "page_height": Config.PAGE_HEIGHT,
        "page": Config.PAGE,
        "position_x": position_x,
        "position_y": position_y,
        "type": pin_type,
    }


@when("eu adiciono pins de assinatura, rubrica e selo ao documento")
def adicionar_pins(context) -> None:  # noqa: ANN001
    document_uuid = context.document_uuid
    if not document_uuid:
        raise AssertionError("document_uuid ausente")

    email = getattr(context, "signer_email", None) or Config.EMAIL_TESTE
    pins_defs = (Config.PIN_SIGNATURE, Config.PIN_RUBRIC, Config.PIN_SEAL)
    last_response = None
    for pos_x, pos_y, pin_type in pins_defs:
        pin = _pin_dict(email, pos_x, pos_y, pin_type, document_uuid)
        last_response = context.pins_service.add_pins(document_uuid, [pin])
        assert_status(last_response, 200)

    context.response = last_response
    context.response_json = last_response.json() if last_response else None


@when("eu replico um pin em todas as páginas do documento")
def replicar_pin(context) -> None:  # noqa: ANN001
    document_uuid = context.document_uuid
    if not document_uuid:
        raise AssertionError("document_uuid ausente")

    email = getattr(context, "signer_email", None) or Config.EMAIL_TESTE
    pos_x, pos_y, pin_type = Config.PIN_SIGNATURE
    pin = {
        "email": email,
        "page_height": Config.PAGE_HEIGHT,
        "page_width": Config.PAGE_WIDTH,
        "position_x": pos_x,
        "position_y": pos_y,
        "type": pin_type,
    }
    response = context.pins_service.add_pins_with_replicas(document_uuid, pin)
    context.response = response
    context.response_json = response.json()
