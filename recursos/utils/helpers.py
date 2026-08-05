"""Utilitários de arquivo para uploads (base64, hashes)."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path


def file_to_base64(file_path: str | Path) -> str:
    path = Path(file_path)
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def file_sha256(file_path: str | Path) -> str:
    return hashlib.sha256(Path(file_path).read_bytes()).hexdigest()


def file_sha512(file_path: str | Path) -> str:
    return hashlib.sha512(Path(file_path).read_bytes()).hexdigest()


def ensure_file_exists(file_path: str | Path) -> Path:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de teste não encontrado: {path}")
    return path
