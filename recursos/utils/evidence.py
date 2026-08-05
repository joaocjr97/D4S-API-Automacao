"""Evidências de API para Allure e arquivos locais.

Anexa request/response (headers mascarados, payload, JSON, tempo)
ao relatório Allure ao final de cada cenário.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from recursos.utils.config import Config
from recursos.utils.logger import mask_headers
from services.base_client import ApiResponse

try:
    import allure
except ImportError:  # pragma: no cover
    allure = None  # type: ignore[assignment]


class ApiEvidence:
    """Coleta e publica evidências HTTP do cenário."""

    def __init__(self) -> None:
        self._reports = Config.reports_dir()
        self._http_dir = self._reports / "http"
        self._http_dir.mkdir(parents=True, exist_ok=True)
        self._calls: list[dict[str, Any]] = []
        self._scenario_slug = ""

    @staticmethod
    def _slug(name: str) -> str:
        slug = re.sub(r"[^\w\-]+", "_", name, flags=re.UNICODE).strip("_")
        return slug[:120] or "cenario"

    def start_scenario(self, scenario_name: str) -> None:
        self._scenario_slug = self._slug(scenario_name)
        self._calls = []

    def record_call(
        self,
        *,
        method: str,
        url: str,
        request_headers: dict[str, Any] | None,
        request_body: Any,
        response: ApiResponse,
    ) -> None:
        entry = {
            "method": method.upper(),
            "url": url,
            "request_headers": mask_headers(request_headers),
            "request_body": request_body,
            "status_code": response.status_code,
            "elapsed_seconds": round(response.elapsed_seconds, 3),
            "response_headers": dict(response.headers),
            "response_body": _safe_json_or_text(response),
        }
        self._calls.append(entry)

    def ingest_client_history(self, history: list[dict[str, Any]]) -> None:
        """Importa o histórico acumulado no BaseClient durante o cenário."""
        for item in history:
            self._calls.append(item)

    def publish(self, scenario_name: str, *, failed: bool = False) -> Path | None:
        """Grava evidência em disco e anexa no Allure."""
        if not self._calls:
            # Fallback: nada registrado via client history
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._slug(scenario_name)}_{timestamp}.json"
        path = self._http_dir / filename
        payload = {
            "scenario": scenario_name,
            "failed": failed,
            "calls": self._calls,
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        if allure is not None:
            allure.attach(
                path.read_text(encoding="utf-8"),
                name="http-calls",
                attachment_type=allure.attachment_type.JSON,
            )
            # Anexa a última chamada em partes para facilitar leitura no report
            last = self._calls[-1]
            _attach_text("request-method-url", f"{last['method']} {last['url']}")
            _attach_json("request-headers", last.get("request_headers"))
            _attach_json("request-body", last.get("request_body"))
            _attach_text(
                "response-status",
                f"{last['status_code']} ({last['elapsed_seconds']}s)",
            )
            _attach_json("response-headers", last.get("response_headers"))
            _attach_json("response-body", last.get("response_body"))

        return path

    def clear(self) -> None:
        self._calls = []


def _safe_json_or_text(response: ApiResponse) -> Any:
    try:
        return response.json()
    except Exception:  # noqa: BLE001
        text = response.text
        if len(text) > 8000:
            return text[:8000] + "… [truncated]"
        return text


def _attach_text(name: str, content: str) -> None:
    if allure is None:
        return
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def _attach_json(name: str, content: Any) -> None:
    if allure is None:
        return
    text = json.dumps(content, ensure_ascii=False, indent=2, default=str)
    allure.attach(text, name=name, attachment_type=allure.attachment_type.JSON)
