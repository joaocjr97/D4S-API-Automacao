"""Gera .env no CI a partir de variáveis de ambiente / secrets."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / ".env.exemplo"
ENV_FILE = ROOT / ".env"

OVERRIDES = {
    "ENVIRONMENT": os.environ.get("ENVIRONMENT", "homol"),
    "D4S_USERNAME": os.environ.get("D4S_USERNAME", ""),
    "D4S_PASSWORD": os.environ.get("D4S_PASSWORD", ""),
    "TOKEN_API": os.environ.get("TOKEN_API", ""),
    "CRYPT_KEY": os.environ.get("CRYPT_KEY", ""),
    "EMAIL_TESTE": os.environ.get("EMAIL_TESTE", ""),
    "EMAIL_ALTERADO": os.environ.get("EMAIL_ALTERADO", "signatario.alterado@teste.com"),
    "WHATSAPP_TESTE": os.environ.get("WHATSAPP_TESTE", ""),
    "UUID_SAFE": os.environ.get("UUID_SAFE", ""),
    "LIST_ESPECIFIC_DOCUMENT": os.environ.get("LIST_ESPECIFIC_DOCUMENT", ""),
    "UUID_PINS": os.environ.get("UUID_PINS", ""),
    "UUID_WEBHOOK_DOCUMENT": os.environ.get("UUID_WEBHOOK_DOCUMENT", ""),
    "UUID_DOC_WEBHOOK": os.environ.get("UUID_DOC_WEBHOOK", ""),
    "URL_WEBHOOK": os.environ.get(
        "URL_WEBHOOK",
        "https://superteste.requestcatcher.com",
    ),
    "DOCUMENTS_PHASE": os.environ.get("DOCUMENTS_PHASE", "3"),
    "TEMPLATE_ID_WORD": os.environ.get("TEMPLATE_ID_WORD", ""),
    "TEMPLATE_ID_HTML": os.environ.get("TEMPLATE_ID_HTML", ""),
    "HTTP_TIMEOUT": os.environ.get("HTTP_TIMEOUT", "30"),
    "HTTP_MAX_RETRIES": os.environ.get("HTTP_MAX_RETRIES", "3"),
    "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
}


def main() -> int:
    if not ENV_EXAMPLE.exists():
        print(f"Arquivo não encontrado: {ENV_EXAMPLE}", file=sys.stderr)
        return 1

    lines: list[str] = []
    for raw in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            lines.append(raw)
            continue
        key = raw.split("=", 1)[0].strip()
        if key in OVERRIDES:
            lines.append(f"{key}={OVERRIDES[key]}")
        else:
            lines.append(raw)

    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    missing = [key for key in ("TOKEN_API", "CRYPT_KEY") if not OVERRIDES.get(key)]
    if missing:
        print(f"Secrets ausentes: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f".env criado em {ENV_FILE}")
    print(f"ENVIRONMENT={OVERRIDES['ENVIRONMENT']}")
    print(f"UUID_SAFE configurado={bool(OVERRIDES['UUID_SAFE'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
