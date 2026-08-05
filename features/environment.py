"""Hooks do Behave — bootstrap do contexto de teste."""

from __future__ import annotations

import os
import sys

# Evita a criação de pastas __pycache__ ao rodar a suíte.
sys.dont_write_bytecode = True

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from behave.runner import Context

from recursos.utils.config import Config
from recursos.utils.data_factory import DataFactory
from recursos.utils.evidence import ApiEvidence
from recursos.utils.logger import get_logger, setup_logger
from services.base_client import BaseClient, create_client
from services.documents_service import DocumentsService
from services.pins_service import PinsService
from services.safes_service import SafesService
from services.signers_service import SignersService
from services.templates_service import TemplatesService
from services.webhooks_service import WebhooksService

# Registra step definitions em subpastas (mesmo padrão do template web)
import features.steps.common.response_steps as _response_steps  # noqa: F401
import features.steps.documents.listagens_steps as _documents_listagens  # noqa: F401
import features.steps.documents.uploads_steps as _documents_uploads  # noqa: F401
import features.steps.pins.pins_steps as _pins_steps  # noqa: F401
import features.steps.safes.listagens_steps as _safes_listagens  # noqa: F401
import features.steps.signers.signers_steps as _signers_steps  # noqa: F401
import features.steps.templates.templates_steps as _templates_steps  # noqa: F401
import features.steps.webhooks.webhooks_steps as _webhooks_steps  # noqa: F401


def before_all(context: Context) -> None:
    """Inicializa config, logger, factory, client e services."""
    env_override = context.config.userdata.get("env") or os.getenv("ENV")
    Config.load(env_override=env_override)

    context.env_name = Config.ENVIRONMENT
    context.config_summary = Config.summary()
    context.logger = setup_logger(level=Config.LOG_LEVEL)
    context.data_factory = DataFactory()
    context.evidence = ApiEvidence()
    context.logger.info(
        "Suite iniciada | env=%s | base_url=%s | token_ok=%s",
        Config.ENVIRONMENT,
        Config.base_url(),
        Config.summary()["has_token_api"],
    )

    try:
        context.client = create_client(require_credentials=True)
    except RuntimeError as exc:
        context.logger.warning("BaseClient sem credenciais: %s", exc)
        context.client = create_client(require_credentials=False)

    context.documents_service = DocumentsService(context.client)
    context.safes_service = SafesService(context.client)
    context.signers_service = SignersService(context.client)
    context.pins_service = PinsService(context.client)
    context.webhooks_service = WebhooksService(context.client)
    context.templates_service = TemplatesService(context.client)


def before_scenario(context: Context, scenario) -> None:  # noqa: ANN001
    """Reseta estado por cenário."""
    context.response = None
    context.response_json = None
    context.document_uuid = None
    context.key_signer = None
    context.signer_email = None
    context.signer_email_alterado = None
    context.signer_whatsapp = None

    client: BaseClient | None = getattr(context, "client", None)
    if client is not None:
        client.clear_history()

    evidence: ApiEvidence | None = getattr(context, "evidence", None)
    if evidence is not None:
        evidence.start_scenario(scenario.name)

    logger = getattr(context, "logger", None) or get_logger()
    logger.info("Cenário: %s", scenario.name)


def after_scenario(context: Context, scenario) -> None:  # noqa: ANN001
    """Publica evidências HTTP (Allure + JSON local)."""
    logger = getattr(context, "logger", None) or get_logger()
    failed = scenario.status.name.lower() not in {"passed", "skipped"}
    status = (
        "PASSED" if scenario.status.name == "passed" else scenario.status.name.upper()
    )

    evidence: ApiEvidence | None = getattr(context, "evidence", None)
    client: BaseClient | None = getattr(context, "client", None)
    if evidence is not None and client is not None:
        evidence.ingest_client_history(client.history)
        path = evidence.publish(scenario.name, failed=failed)
        if path is not None:
            logger.info("Evidência HTTP: %s", path)

    logger.info("Fim do cenário [%s]: %s", status, scenario.name)


def after_all(context: Context) -> None:
    """Encerra recursos globais."""
    client: BaseClient | None = getattr(context, "client", None)
    if client is not None:
        client.close()

    logger = getattr(context, "logger", None) or get_logger()
    logger.info("Suite finalizada | env=%s", getattr(context, "env_name", "?"))
