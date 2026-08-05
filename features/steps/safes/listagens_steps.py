"""Steps de listagens de cofres."""

from __future__ import annotations

from behave import when


@when("eu consulto todos os cofres da conta")
def listar_todos_cofres(context) -> None:  # noqa: ANN001
    context.response = context.safes_service.list_all()
    context.response_json = context.response.json()
