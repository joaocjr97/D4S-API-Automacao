"""Assertions reutilizáveis para respostas da API.

Os Steps devem usar estas funções em vez de asserts soltos.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from services.base_client import ApiResponse

UUID_V4_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def assert_status(response: ApiResponse, expected: int | list[int]) -> None:
    """Valida status HTTP."""
    allowed = {expected} if isinstance(expected, int) else set(expected)
    if response.status_code not in allowed:
        raise AssertionError(
            f"Status inesperado: {response.status_code} "
            f"(esperado {sorted(allowed)}) em {response.method} {response.url}. "
            f"Body: {response.text[:500]}"
        )


def assert_equals(actual: Any, expected: Any, message: str | None = None) -> None:
    if actual != expected:
        prefix = f"{message}: " if message else ""
        raise AssertionError(f"{prefix}esperado={expected!r}, obtido={actual!r}")


def assert_contains(
    container: Any,
    expected: Any,
    message: str | None = None,
) -> None:
    if expected not in container:
        prefix = f"{message}: " if message else ""
        raise AssertionError(f"{prefix}{expected!r} não encontrado em {container!r}")


def assert_not_empty(value: Any, message: str | None = None) -> None:
    if value is None or value == "" or value == [] or value == {}:
        prefix = f"{message}: " if message else ""
        raise AssertionError(f"{prefix}valor vazio: {value!r}")


def assert_header(
    response: ApiResponse,
    header_name: str,
    expected: str | None = None,
    *,
    contains: str | None = None,
) -> None:
    """Valida existência / valor de um header (case-insensitive)."""
    headers = {key.lower(): value for key, value in response.headers.items()}
    key = header_name.lower()
    if key not in headers:
        raise AssertionError(
            f"Header '{header_name}' ausente. Headers: {list(response.headers)}"
        )
    actual = headers[key]
    if expected is not None and actual != expected:
        raise AssertionError(
            f"Header '{header_name}': esperado={expected!r}, obtido={actual!r}"
        )
    if contains is not None and contains not in actual:
        raise AssertionError(
            f"Header '{header_name}' não contém {contains!r}. Valor: {actual!r}"
        )


def assert_response_time(
    response: ApiResponse,
    max_seconds: float,
    message: str | None = None,
) -> None:
    if response.elapsed_seconds > max_seconds:
        prefix = f"{message}: " if message else ""
        raise AssertionError(
            f"{prefix}tempo {response.elapsed_seconds:.3f}s "
            f"excede o limite de {max_seconds}s"
        )


def assert_json_schema(
    response: ApiResponse,
    schema: dict[str, Any] | Path | str,
) -> None:
    """Valida o JSON da resposta contra um JSON Schema."""
    payload = response.json()
    schema_data = _load_schema(schema)
    validator = Draft202012Validator(schema_data)
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, err.path)) or '<root>'}: {err.message}"
            for err in errors[:5]
        )
        raise AssertionError(f"JSON Schema inválido: {details}")


def assert_message(response: ApiResponse, expected: str) -> None:
    """Valida o campo `message` típico das respostas D4Sign."""
    payload = response.json()
    if not isinstance(payload, dict):
        raise AssertionError(f"Body não é objeto JSON: {payload!r}")
    assert_equals(payload.get("message"), expected, message="campo message")


def assert_uuid(value: str, message: str | None = None) -> None:
    assert_not_empty(value, message=message or "uuid")
    if not UUID_V4_PATTERN.match(str(value)):
        prefix = f"{message}: " if message else ""
        raise AssertionError(f"{prefix}UUID inválido: {value!r}")


def assert_success_upload(response: ApiResponse) -> str:
    """Valida upload típico (status 200, message=success, uuid válido) e retorna o uuid."""
    assert_status(response, 200)
    assert_not_empty(response.text, message="body da resposta")
    payload = response.json()
    assert_equals(payload.get("message"), "success", message="campo message")
    uuid_value = payload.get("uuid")
    assert_uuid(uuid_value, message="uuid do documento")
    return str(uuid_value)


def assert_json_path_equals(
    response: ApiResponse,
    path: str,
    expected: Any,
) -> None:
    """Valida valor em caminho simples com notação ponto (ex.: message.0.email)."""
    actual = _resolve_path(response.json(), path)
    assert_equals(actual, expected, message=f"path '{path}'")


def _load_schema(schema: dict[str, Any] | Path | str) -> dict[str, Any]:
    if isinstance(schema, dict):
        return schema
    path = Path(schema)
    if not path.is_file():
        raise AssertionError(f"Schema não encontrado: {path}")
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if current is None:
            raise AssertionError(f"Path '{path}' inválido (encontrou None em '{part}')")
        if part.isdigit():
            index = int(part)
            if not isinstance(current, list) or index >= len(current):
                raise AssertionError(f"Path '{path}' inválido no índice [{index}]")
            current = current[index]
        else:
            if not isinstance(current, dict) or part not in current:
                raise AssertionError(f"Path '{path}' inválido na chave '{part}'")
            current = current[part]
    return current


__all__ = [
    "assert_status",
    "assert_equals",
    "assert_contains",
    "assert_not_empty",
    "assert_header",
    "assert_response_time",
    "assert_json_schema",
    "assert_message",
    "assert_uuid",
    "assert_success_upload",
    "assert_json_path_equals",
    "UUID_V4_PATTERN",
]
