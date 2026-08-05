"""Geração de massa de dados dinâmica com Faker.

Evita dados fixos sempre que possível. IDs de ambiente (UUID_SAFE, templates)
continuam vindo do Config/.env.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from faker import Faker

_faker = Faker("pt_BR")
Faker.seed(None)


@dataclass
class SignerData:
    email: str
    act: int = 1
    foreign: int = 0
    certificadoicpbr: int = 0
    assinatura_presencial: int = 0
    docauth: int = 0
    docauthandselfie: int = 0
    embed_methodauth: str = ""
    embed_smsnumber: str = ""
    upload_allow: int = 0
    upload_obs: str = ""
    whatsapp_number: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PinData:
    email: str
    page_width: int = 794
    page_height: int = 1123
    page: int = 1
    position_x: int = 100
    position_y: int = 150
    type: int = 0  # 0 assinatura, 1 rubrica, 2 selo

    def to_dict(self, *, document_uuid: str | None = None) -> dict[str, Any]:
        payload = asdict(self)
        if document_uuid:
            payload["document"] = document_uuid
        return payload


@dataclass
class DocumentNameData:
    name: str
    mime_type: str = "application/pdf"


class DataFactory:
    """Factory de payloads para testes de API D4Sign."""

    def __init__(self, locale: str = "pt_BR") -> None:
        self.faker = Faker(locale)

    # ------------------------------------------------------------------
    # Pessoas / contatos
    # ------------------------------------------------------------------

    def email(self, domain: str = "teste-d4sign.local") -> str:
        local = self.faker.user_name().replace(".", "_")
        stamp = self.faker.unique.random_int(min=1000, max=99999)
        return f"{local}_{stamp}@{domain}"

    def phone_br(self) -> str:
        """Telefone no formato E.164 BR (ex.: 55119XXXXXXXX)."""
        suffix = self.faker.numerify("9########")
        return f"5511{suffix}"

    def cpf(self) -> str:
        return self.faker.cpf()

    def cnpj(self) -> str:
        return self.faker.cnpj()

    def person_name(self) -> str:
        return self.faker.name()

    def company_name(self) -> str:
        return self.faker.company()

    # ------------------------------------------------------------------
    # Signatários
    # ------------------------------------------------------------------

    def signer_by_email(self, email: str | None = None, *, act: int = 1) -> SignerData:
        return SignerData(email=email or self.email(), act=act)

    def signer_by_whatsapp(
        self,
        whatsapp_number: str | None = None,
        *,
        act: int = 1,
    ) -> SignerData:
        return SignerData(
            email="",
            act=act,
            whatsapp_number=whatsapp_number or self.phone_br(),
        )

    def signers_payload(self, *signers: SignerData) -> dict[str, list[dict[str, Any]]]:
        return {"signers": [signer.to_dict() for signer in signers]}

    # ------------------------------------------------------------------
    # Documentos / pins / templates
    # ------------------------------------------------------------------

    def document_name(self, prefix: str = "Documento QA") -> DocumentNameData:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return DocumentNameData(name=f"{prefix} {stamp}")

    def pin(
        self,
        email: str | None = None,
        *,
        position_x: int | None = None,
        position_y: int | None = None,
        pin_type: int = 0,
        page: int = 1,
    ) -> PinData:
        return PinData(
            email=email or self.email(),
            page=page,
            position_x=position_x if position_x is not None else self.faker.random_int(50, 700),
            position_y=position_y if position_y is not None else self.faker.random_int(50, 1000),
            type=pin_type,
        )

    def pins_payload(
        self,
        *pins: PinData,
        document_uuid: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            "pins": [pin.to_dict(document_uuid=document_uuid) for pin in pins]
        }

    def replicate_pin_payload(self, pin: PinData) -> dict[str, dict[str, Any]]:
        """Payload para /addpinswithreplics (objeto único em `pins`)."""
        data = pin.to_dict()
        data.pop("page", None)
        data.pop("document", None)
        return {"pins": data}

    def change_email_payload(
        self,
        *,
        email_before: str,
        email_after: str,
        key_signer: str,
    ) -> dict[str, str]:
        return {
            "email-before": email_before,
            "email-after": email_after,
            "key-signer": key_signer,
        }

    def remove_signer_payload(
        self,
        *,
        email_signer: str,
        key_signer: str,
    ) -> dict[str, str]:
        return {
            "email-signer": email_signer,
            "key-signer": key_signer,
        }

    def send_to_signer_payload(
        self,
        *,
        skip_email: int = 1,
        workflow: int = 0,
        message: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "skip_email": skip_email,
            "workflow": workflow,
        }
        if message:
            payload["message"] = message
        return payload

    def webhook_payload(self, url: str | None = None) -> dict[str, str]:
        return {"url": url or f"https://{self.faker.domain_name()}/hooks/d4sign"}

    def html_template_vars(self) -> dict[str, str]:
        return {
            "marca": self.faker.word().title(),
            "laranja": self.faker.word().title(),
            "cor": self.faker.color_name(),
            "trueFALSE": self.faker.random_element(elements=("true", "false")),
            "rua": self.faker.street_name(),
            "lugares": self.faker.city(),
            "restaurant": self.faker.company(),
        }

    def word_template_vars(self) -> dict[str, str]:
        return {
            "nome_razao_social": self.company_name(),
            "PF_PF": "Pessoa Jurídica",
            "CNPJ_CPF": self.cnpj(),
            "rua_numero": f"{self.faker.street_name()}, {self.faker.building_number()}",
            "bairro": self.faker.city_suffix(),
            "cidade": self.faker.city(),
            "Estado_UF": self.faker.estado_sigla(),
            "cep": self.faker.postcode(),
            "veiculo1": "Veículo Leve",
            "Valor_Veic1": f"{self.faker.random_int(100, 500)},00",
            "qtdveic1": str(self.faker.random_int(1, 20)),
            "veiculo2": "Veículo Utilitário",
            "Valor_Veic2": f"{self.faker.random_int(100, 500)},00",
            "qtdveic2": str(self.faker.random_int(1, 20)),
            "veiculo3": "Motocicleta",
            "Valor_Veic3": f"{self.faker.random_int(100, 500)},00",
            "qtdveic3": str(self.faker.random_int(1, 20)),
            "datainicialcontrato": datetime.now().strftime("%d de %B de %Y"),
            "RAZAOSOCIAL_NOME": self.company_name(),
            "tipopjoupf": "PJ",
            "nomerepresentante": self.person_name(),
            "cpfrepresentante": self.cpf(),
        }


# Instância padrão para import direto nos steps/services
data_factory = DataFactory()
