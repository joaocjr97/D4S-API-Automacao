"""Configuração central do projeto — carrega variáveis do .env.

Espelha o padrão de `template-web-tests-python/recursos/utils/config.py`,
adaptado para testes de API (BASE_URL com /api/v1, timeouts HTTP, UUIDs).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    _loaded = False

    ENVIRONMENT: str = "homol"
    USERNAME: str = ""
    PASSWORD: str = ""
    TOKEN_API: str = ""
    CRYPT_KEY: str = ""
    EMAIL_TESTE: str = ""
    EMAIL_ALTERADO: str = ""
    WHATSAPP_TESTE: str = ""

    UUID_SAFE: str = ""
    LIST_ESPECIFIC_DOCUMENT: str = ""
    UUID_PINS: str = ""
    UUID_WEBHOOK_DOCUMENT: str = ""
    UUID_DOC_WEBHOOK: str = ""
    URL_WEBHOOK: str = "https://superteste.requestcatcher.com"
    DOCUMENTS_PHASE: str = "3"

    TEMPLATE_ID_WORD: str = ""
    TEMPLATE_NAME_WORD: str = "Template Word de Testes QA.docx"
    TEMPLATE_ID_HTML: str = ""
    TEMPLATE_NAME_HTML: str = "Relatório de QA - Temp HTML"

    PAGE_WIDTH: int = 794
    PAGE_HEIGHT: int = 1123
    PAGE: int = 1
    PIN_SIGNATURE: tuple[int, int, int] = (100, 150, 0)
    PIN_RUBRIC: tuple[int, int, int] = (397, 300, 1)
    PIN_SEAL: tuple[int, int, int] = (600, 500, 2)

    # Expectativas do cenário de listagem de pins (ambiente-específico)
    EXPECTED_PIN_EMAIL: str = ""
    EXPECTED_PIN_POSITION_X: int = 600
    EXPECTED_PIN_PAGE_HEIGHT: str = "1123.00"

    HTTP_TIMEOUT: float = 30.0
    HTTP_MAX_RETRIES: int = 3
    LOG_LEVEL: str = "INFO"

    # Hosts web → a API usa o mesmo host com sufixo /api/v1
    URLS = {
        "ghost": "https://ghost.d4sign.com.br",
        "homol": "https://homol.d4sign.com.br",
        "staging": "https://stage.d4sign.com.br",
        "hotfix": "https://hotfix.d4sign.com.br",
        "prod": "https://secure.d4sign.com.br",
    }

    @classmethod
    def load(cls, env_override: str | None = None) -> None:
        """Carrega o .env uma única vez.

        Args:
            env_override: sobrescreve ENVIRONMENT (ex.: userdata do Behave `-D env=hml`).
        """
        if cls._loaded and env_override is None:
            return

        root = cls.project_root()
        load_dotenv(root / ".env", override=True)

        environment = (
            env_override
            or os.getenv("ENVIRONMENT")
            or os.getenv("ENV")
            or "homol"
        ).lower()

        # Alias usados no Robot / userdata Behave
        aliases = {"hml": "homol", "dev": "ghost", "development": "ghost"}
        cls.ENVIRONMENT = aliases.get(environment, environment)

        cls.USERNAME = os.getenv("D4S_USERNAME") or os.getenv("USERNAME", "")
        cls.PASSWORD = os.getenv("D4S_PASSWORD") or os.getenv("PASSWORD", "")
        cls.TOKEN_API = os.getenv("TOKEN_API", "")
        cls.CRYPT_KEY = os.getenv("CRYPT_KEY", "")
        cls.EMAIL_TESTE = os.getenv("EMAIL_TESTE", "")
        cls.EMAIL_ALTERADO = os.getenv(
            "EMAIL_ALTERADO",
            "signatario.alterado@teste.com",
        )
        cls.WHATSAPP_TESTE = os.getenv("WHATSAPP_TESTE", "")

        cls.UUID_SAFE = os.getenv("UUID_SAFE", "")
        cls.LIST_ESPECIFIC_DOCUMENT = os.getenv("LIST_ESPECIFIC_DOCUMENT", "")
        cls.UUID_PINS = os.getenv("UUID_PINS", "")
        cls.UUID_WEBHOOK_DOCUMENT = os.getenv("UUID_WEBHOOK_DOCUMENT", "")
        cls.UUID_DOC_WEBHOOK = os.getenv("UUID_DOC_WEBHOOK", "")
        cls.URL_WEBHOOK = os.getenv(
            "URL_WEBHOOK",
            "https://superteste.requestcatcher.com",
        )
        cls.DOCUMENTS_PHASE = os.getenv("DOCUMENTS_PHASE", "3")

        cls.TEMPLATE_ID_WORD = os.getenv("TEMPLATE_ID_WORD", "")
        cls.TEMPLATE_NAME_WORD = os.getenv(
            "TEMPLATE_NAME_WORD",
            "Template Word de Testes QA.docx",
        )
        cls.TEMPLATE_ID_HTML = os.getenv("TEMPLATE_ID_HTML", "")
        cls.TEMPLATE_NAME_HTML = os.getenv(
            "TEMPLATE_NAME_HTML",
            "Relatório de QA - Temp HTML",
        )

        cls.PAGE_WIDTH = int(os.getenv("PAGE_WIDTH", "794"))
        cls.PAGE_HEIGHT = int(os.getenv("PAGE_HEIGHT", "1123"))
        cls.PAGE = int(os.getenv("PAGE", "1"))
        cls.PIN_SIGNATURE = (
            int(os.getenv("POS_X_0", "100")),
            int(os.getenv("POS_Y_0", "150")),
            int(os.getenv("TYPE_0", "0")),
        )
        cls.PIN_RUBRIC = (
            int(os.getenv("POS_X_1", "397")),
            int(os.getenv("POS_Y_1", "300")),
            int(os.getenv("TYPE_1", "1")),
        )
        cls.PIN_SEAL = (
            int(os.getenv("POS_X_2", "600")),
            int(os.getenv("POS_Y_2", "500")),
            int(os.getenv("TYPE_2", "2")),
        )

        cls.EXPECTED_PIN_EMAIL = os.getenv("EXPECTED_PIN_EMAIL", "")
        cls.EXPECTED_PIN_POSITION_X = int(os.getenv("EXPECTED_PIN_POSITION_X", "600"))
        cls.EXPECTED_PIN_PAGE_HEIGHT = os.getenv("EXPECTED_PIN_PAGE_HEIGHT", "1123.00")

        cls.HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30"))
        cls.HTTP_MAX_RETRIES = int(os.getenv("HTTP_MAX_RETRIES", "3"))
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        cls._loaded = True

    @classmethod
    def project_root(cls) -> Path:
        return Path(__file__).resolve().parents[2]

    @classmethod
    def host_url(cls) -> str:
        """URL base do host (sem /api/v1)."""
        return cls.URLS.get(cls.ENVIRONMENT, cls.URLS["prod"]).rstrip("/")

    @classmethod
    def base_url(cls) -> str:
        """URL base da API D4Sign (`…/api/v1`)."""
        override = os.getenv("BASE_URL", "").strip()
        if override:
            return override.rstrip("/")
        return f"{cls.host_url()}/api/v1"

    @classmethod
    def auth_headers(cls) -> dict[str, str]:
        """Headers padrão de autenticação da API D4Sign."""
        return {
            "tokenAPI": cls.TOKEN_API,
            "cryptKey": cls.CRYPT_KEY,
            "Accept": "application/json",
        }

    @classmethod
    def require_api_credentials(cls) -> None:
        """Falha cedo se TOKEN_API / CRYPT_KEY estiverem ausentes."""
        missing = [
            name
            for name, value in (
                ("TOKEN_API", cls.TOKEN_API),
                ("CRYPT_KEY", cls.CRYPT_KEY),
            )
            if not value or value.startswith("sua_")
        ]
        if missing:
            raise RuntimeError(
                "Credenciais de API ausentes no .env: "
                + ", ".join(missing)
                + ". Copie .env.exemplo para .env e preencha os valores."
            )

    @classmethod
    def test_file(cls, filename: str) -> Path:
        return (cls.project_root() / "data" / "files" / filename).resolve()

    @classmethod
    def doc_testes_pdf(cls) -> Path:
        return cls.test_file("doc-testes.pdf")

    @classmethod
    def reports_dir(cls) -> Path:
        path = cls.project_root() / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def summary(cls) -> dict[str, str | float | int]:
        """Resumo seguro para logs (sem secrets)."""
        return {
            "environment": cls.ENVIRONMENT,
            "base_url": cls.base_url(),
            "http_timeout": cls.HTTP_TIMEOUT,
            "http_max_retries": cls.HTTP_MAX_RETRIES,
            "log_level": cls.LOG_LEVEL,
            "has_token_api": bool(cls.TOKEN_API) and not cls.TOKEN_API.startswith("sua_"),
            "has_crypt_key": bool(cls.CRYPT_KEY) and not cls.CRYPT_KEY.startswith("sua_"),
        }
