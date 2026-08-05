"""Cliente HTTP base da suíte — único ponto de saída para a API D4Sign.

Responsabilidades:
- Base URL, timeout e headers padrão (auth tokenAPI/cryptKey)
- Retry em falhas transitórias de rede / 5xx
- Logs estruturados de request e response
- Tratamento de erros com mensagens diagnósticas

Todos os Services devem usar este cliente. Steps nunca chamam HTTPX direto.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from recursos.utils.config import Config
from recursos.utils.logger import get_logger, log_request, log_response, mask_headers, setup_logger


class ApiClientError(Exception):
    """Erro de infraestrutura HTTP (rede, timeout, etc.)."""


class ApiResponseError(Exception):
    """Resposta HTTP recebida, porém com status inesperado ou corpo inválido."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: ApiResponse | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


@dataclass
class ApiResponse:
    """Wrapper fino sobre a resposta HTTPX para uso nos Services/assertions."""

    status_code: int
    headers: dict[str, str]
    text: str
    elapsed_seconds: float
    url: str
    method: str
    _json: Any = field(default=None, repr=False)
    _raw: httpx.Response | None = field(default=None, repr=False)

    def json(self) -> Any:
        if self._json is not None:
            return self._json
        if not self.text:
            self._json = None
            return None
        try:
            self._json = json.loads(self.text)
        except json.JSONDecodeError as exc:
            raise ApiResponseError(
                f"Resposta não é JSON válido: {exc}",
                status_code=self.status_code,
                response=self,
            ) from exc
        return self._json

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class _RetryableStatusError(Exception):
    """Marcador interno para acionar retry em status 5xx."""

    def __init__(self, message: str, response: httpx.Response) -> None:
        super().__init__(message)
        self.response = response


class BaseClient:
    """Cliente HTTP compartilhado por todos os Services."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
        verify_ssl: bool = True,
    ) -> None:
        if not Config._loaded:
            Config.load()

        self.base_url = (base_url or Config.base_url()).rstrip("/")
        self.timeout = timeout if timeout is not None else Config.HTTP_TIMEOUT
        self.max_retries = (
            max_retries if max_retries is not None else Config.HTTP_MAX_RETRIES
        )
        self.default_headers = {
            **Config.auth_headers(),
            **(default_headers or {}),
        }
        self.logger = setup_logger(level=Config.LOG_LEVEL)
        self.history: list[dict[str, Any]] = []
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            headers=self.default_headers,
            verify=verify_ssl,
            follow_redirects=True,
        )

    def clear_history(self) -> None:
        self.history.clear()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BaseClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | list[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "GET",
            path,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    def post(
        self,
        path: str,
        *,
        json_body: Any = None,
        data: Any = None,
        files: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | list[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "POST",
            path,
            json_body=json_body,
            data=data,
            files=files,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    def put(
        self,
        path: str,
        *,
        json_body: Any = None,
        data: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | list[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "PUT",
            path,
            json_body=json_body,
            data=data,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    def delete(
        self,
        path: str,
        *,
        json_body: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | list[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "DELETE",
            path,
            json_body=json_body,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        data: Any = None,
        files: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | list[int] | None = None,
    ) -> ApiResponse:
        """Executa a chamada HTTP com retry, logs e validação opcional de status."""
        url_path = path if path.startswith("/") else f"/{path}"
        merged_headers = {**self.default_headers, **(headers or {})}

        # Multipart: deixa o HTTPX definir o boundary do Content-Type
        if files is not None:
            merged_headers = {
                key: value
                for key, value in merged_headers.items()
                if key.lower() != "content-type"
            }

        log_body: Any
        if files is not None:
            log_body = {
                "files": list(files.keys()) if isinstance(files, dict) else "<multipart>"
            }
        elif json_body is not None:
            log_body = json_body
        else:
            log_body = data

        full_url = f"{self.base_url}{url_path}"
        log_request(
            self.logger,
            method=method,
            url=full_url,
            headers=merged_headers,
            body=log_body,
        )

        started = time.perf_counter()
        try:
            raw = self._send_with_retry(
                method=method.upper(),
                url=url_path,
                params=params,
                headers=merged_headers,
                json_body=json_body,
                data=data,
                files=files,
            )
        except httpx.TimeoutException as exc:
            elapsed = time.perf_counter() - started
            self.logger.error(
                "TIMEOUT %s %s após %.3fs: %s",
                method.upper(),
                full_url,
                elapsed,
                exc,
            )
            raise ApiClientError(
                f"Timeout após {self.timeout}s em {method.upper()} {full_url}"
            ) from exc
        except httpx.HTTPError as exc:
            elapsed = time.perf_counter() - started
            self.logger.error(
                "HTTP_ERROR %s %s após %.3fs: %s",
                method.upper(),
                full_url,
                elapsed,
                exc,
            )
            raise ApiClientError(
                f"Falha de rede em {method.upper()} {full_url}: {exc}"
            ) from exc

        elapsed = time.perf_counter() - started
        response = ApiResponse(
            status_code=raw.status_code,
            headers=dict(raw.headers),
            text=raw.text,
            elapsed_seconds=elapsed,
            url=str(raw.url),
            method=method.upper(),
            _raw=raw,
        )

        try:
            body_for_log: Any = response.json()
        except ApiResponseError:
            body_for_log = response.text

        log_response(
            self.logger,
            method=method,
            url=str(raw.url),
            status_code=raw.status_code,
            headers=dict(raw.headers),
            body=body_for_log,
            elapsed_seconds=elapsed,
        )

        self.history.append(
            {
                "method": method.upper(),
                "url": str(raw.url),
                "request_headers": mask_headers(merged_headers),
                "request_body": log_body,
                "status_code": raw.status_code,
                "elapsed_seconds": round(elapsed, 3),
                "response_headers": dict(raw.headers),
                "response_body": body_for_log,
            }
        )

        if expected_status is not None:
            allowed = (
                {expected_status}
                if isinstance(expected_status, int)
                else set(expected_status)
            )
            if response.status_code not in allowed:
                raise ApiResponseError(
                    f"Status inesperado: {response.status_code} "
                    f"(esperado {sorted(allowed)}) em {method.upper()} {raw.url}. "
                    f"Body: {response.text[:500]}",
                    status_code=response.status_code,
                    response=response,
                )

        return response

    def _send_with_retry(
        self,
        *,
        method: str,
        url: str,
        params: dict[str, Any] | None,
        headers: dict[str, str],
        json_body: Any,
        data: Any,
        files: Any,
    ) -> httpx.Response:
        """Retry em erros de transporte e 5xx; devolve a última resposta 5xx se esgotar."""

        @retry(
            reraise=True,
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
            retry=retry_if_exception_type(
                (httpx.TransportError, _RetryableStatusError)
            ),
        )
        def _do_request() -> httpx.Response:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json_body,
                data=data,
                files=files,
            )
            if response.status_code >= 500:
                self.logger.warning(
                    "Retryable status %s em %s %s",
                    response.status_code,
                    method,
                    response.url,
                )
                raise _RetryableStatusError(
                    f"HTTP {response.status_code}",
                    response=response,
                )
            return response

        try:
            return _do_request()
        except _RetryableStatusError as exc:
            # Após esgotar retries, ainda devolve a resposta para asserts nos testes
            return exc.response


def create_client(*, require_credentials: bool = True) -> BaseClient:
    """Factory usada pelo environment.py / Services."""
    if require_credentials:
        Config.require_api_credentials()
    client = BaseClient()
    get_logger().debug(
        "BaseClient criado | base_url=%s | timeout=%s | retries=%s",
        client.base_url,
        client.timeout,
        client.max_retries,
    )
    return client
