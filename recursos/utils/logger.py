"""Logging estruturado para diagnóstico de falhas de API.

Registra request/response com método, URL, headers (mascarados), body e tempo.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

# Campos sensíveis nunca aparecem em texto puro nos logs
_SENSITIVE_KEYS = {
    "tokenapi",
    "cryptkey",
    "authorization",
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
}


def _mask_value(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    if len(text) <= 8:
        return "***"
    return f"{text[:4]}…{text[-2:]}***"


def mask_headers(headers: dict[str, Any] | None) -> dict[str, Any]:
    """Retorna cópia dos headers com valores sensíveis mascarados."""
    if not headers:
        return {}
    masked: dict[str, Any] = {}
    for key, value in headers.items():
        if key.lower().replace("-", "").replace("_", "") in _SENSITIVE_KEYS or key.lower() in {
            "tokenapi",
            "cryptkey",
            "authorization",
        }:
            masked[key] = _mask_value(value)
        else:
            masked[key] = value
    return masked


def _safe_body(body: Any, max_length: int = 4000) -> Any:
    """Normaliza body para log (dict/list/str), truncando se necessário."""
    if body is None:
        return None
    if isinstance(body, (dict, list)):
        try:
            text = json.dumps(body, ensure_ascii=False, default=str)
        except TypeError:
            text = str(body)
    else:
        text = body if isinstance(body, str) else str(body)

    if len(text) > max_length:
        return text[:max_length] + f"… [truncated {len(text) - max_length} chars]"
    if isinstance(body, (dict, list)):
        return body
    return text


def setup_logger(name: str = "d4sign.api", level: str = "INFO") -> logging.Logger:
    """Configura (ou reutiliza) logger com saída no stdout."""
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return logger


def get_logger(name: str = "d4sign.api") -> logging.Logger:
    return logging.getLogger(name)


def log_request(
    logger: logging.Logger,
    *,
    method: str,
    url: str,
    headers: dict[str, Any] | None = None,
    body: Any = None,
) -> None:
    payload = {
        "event": "http_request",
        "method": method.upper(),
        "url": url,
        "headers": mask_headers(headers),
        "body": _safe_body(body),
    }
    logger.info("REQUEST  %s", json.dumps(payload, ensure_ascii=False, default=str))


def log_response(
    logger: logging.Logger,
    *,
    method: str,
    url: str,
    status_code: int,
    headers: dict[str, Any] | None = None,
    body: Any = None,
    elapsed_seconds: float | None = None,
) -> None:
    payload = {
        "event": "http_response",
        "method": method.upper(),
        "url": url,
        "status_code": status_code,
        "elapsed_seconds": round(elapsed_seconds, 3) if elapsed_seconds is not None else None,
        "headers": mask_headers(headers),
        "body": _safe_body(body),
    }
    level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
    logger.log(
        level,
        "RESPONSE %s",
        json.dumps(payload, ensure_ascii=False, default=str),
    )
