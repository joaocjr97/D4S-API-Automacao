# D4Sign API Tests — Behave + HTTPX

[![Python](https://img.shields.io/badge/python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Behave](https://img.shields.io/badge/BDD-Behave-0B5FFF)](https://behave.readthedocs.io/)
[![HTTPX](https://img.shields.io/badge/HTTP-HTTPX-009688)](https://www.python-httpx.org/)
[![Allure](https://img.shields.io/badge/report-Allure-FF6A5B)](https://docs.qameta.io/allure/)
[![License](https://img.shields.io/badge/uso-interno%20QA-lightgrey)](#)

Suíte de automação de **API** da plataforma **D4Sign** com **Behave (BDD/Gherkin em português)**, **Service Layer** e **HTTPX**.

Repositório: https://github.com/joaocjr97/D4S-API-Automacao.git 


## Sumário

- [Stack](#stack)
- [Cobertura](#cobertura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração (.env)](#configuração-env)
- [Como executar](#como-executar)
- [Tags](#tags)
- [Arquitetura e convenções](#arquitetura-e-convenções)
- [Evidências e relatórios](#evidências-e-relatórios)
- [CI (GitHub Actions)](#ci-github-actions)
- [Tempo de execução](#tempo-de-execução)
- [Troubleshooting](#troubleshooting)
- [Dados de teste](#dados-de-teste)
- [Licença / uso](#licença--uso)

## Stack

| Camada | Tecnologia |
|--------|------------|
| BDD | Behave 1.2.6 + Gherkin (`# language: pt`) |
| HTTP | HTTPX + Tenacity (retry) |
| Padrão | Service Layer (`services/`) + steps finos (`features/steps/`) |
| Config | `python-dotenv` + `recursos/utils/config.py` |
| Dados | Faker + DataFactory |
| Validações | Assertions reutilizáveis (+ JSON Schema opcional) |
| Relatórios | HTML (`behave-html-formatter`), Allure, JSON HTTP em `reports/http/` |
| CI | GitHub Actions (Python 3.13) |
| Qualidade | Ruff + Black |

Não usa requests/urllib3 direto nos steps. O HTTP passa por `BaseClient` (HTTPX), exposto via services no `context`.

## Cobertura

| Área | Feature | Cenários | Tags principais |
|------|---------|----------|-----------------|
| Listagens docs | `documents/listagens.feature` | 6 | `@api` `@documents` `@smoke` `@critical` |
| Listagens cofres | `safes/listagens.feature` | 1 | `@api` `@safes` `@smoke` |
| Uploads | `documents/uploads.feature` | 4 | `@api` `@upload` `@documents` |
| Signatários | `signers/fluxos.feature` | 3 | `@api` `@signature` `@signers` |
| Pins | `pins/pins.feature` | 1 | `@api` `@pins` `@signature` `@critical` |
| Templates | `templates/templates.feature` | 2 | `@api` `@template` `@templates` |
| Webhooks | `webhooks/webhooks.feature` | 1 | `@api` `@webhooks` |
| **Total** | **7 features** | **18** | |

## Estrutura do projeto

```
template-api-tests-python/
├── features/
│   ├── environment.py              # Hooks Behave (client, services, evidências)
│   ├── documents/
│   │   ├── listagens.feature
│   │   └── uploads.feature
│   ├── safes/listagens.feature
│   ├── signers/fluxos.feature
│   ├── pins/pins.feature
│   ├── templates/templates.feature
│   ├── webhooks/webhooks.feature
│   └── steps/
│       ├── common/response_steps.py
│       ├── documents/
│       ├── safes/
│       ├── signers/
│       ├── pins/
│       ├── templates/
│       └── webhooks/
├── services/
│   ├── base_client.py              # HTTPX + retry + histórico
│   ├── documents_service.py
│   ├── safes_service.py
│   ├── signers_service.py
│   ├── pins_service.py
│   ├── templates_service.py
│   └── webhooks_service.py
├── recursos/utils/
│   ├── config.py                   # .env → Config
│   ├── assertions.py               # Status, message, schema, upload…
│   ├── data_factory.py             # Payloads / Faker
│   ├── evidence.py                 # Evidências HTTP → JSON / Allure
│   ├── helpers.py                  # base64, hashes de arquivo
│   ├── logger.py
│   ├── create_env_ci.py            # Gera .env no CI a partir de secrets
│   └── generate_job_summary.py     # Summary do GitHub Actions
├── data/files/                     # PDF usado nos uploads
├── reports/                        # HTML, Allure, http/ (gitignored)
├── .github/workflows/ci.yml
├── behave.ini
├── pyproject.toml
├── requirements.txt
├── .env.exemplo
└── README.md
```

## Pré-requisitos

- Python **3.13+** (alinhado ao `pyproject.toml` / CI)
- `pip`
- Conta de teste na D4Sign com **token API** e **crypt key**
- UUIDs / templates do **mesmo ambiente** do token (homol, ghost, staging…)

## Instalação

```bash
git clone https://github.com/joaocjr97/D4S-API-Automacao.git
cd d4sign-api-tests-playwright

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

# Windows
copy .env.exemplo .env

# Linux / macOS
cp .env.exemplo .env
```

Edite o `.env` com credenciais e UUIDs reais. Prefira ambientes de QA (`homol`, `ghost`, `staging`, `hotfix`). Evite `prod` na automação local, salvo necessidade explícita.

## Configuração (.env)

Copie de `.env.exemplo`. Variáveis principais:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `ENVIRONMENT` | `homol` | `prod`, `ghost`, `homol`, `staging`, `hotfix` |
| `D4S_USERNAME` | — | E-mail (opcional; `D4S_` evita conflito com `USERNAME` do Windows) |
| `D4S_PASSWORD` | — | Senha (opcional para API) |
| `TOKEN_API` | — | Token da API (**obrigatório**) |
| `CRYPT_KEY` | — | Crypt key (**obrigatório**) |
| `EMAIL_TESTE` | — | E-mail do signatário nos fluxos |
| `EMAIL_ALTERADO` | `signatario.alterado@teste.com` | E-mail usado ao alterar signatário |
| `WHATSAPP_TESTE` | — | WhatsApp do signatário |
| `UUID_SAFE` | — | Cofre para upload / templates / signers |
| `LIST_ESPECIFIC_DOCUMENT` | — | UUID do documento (listagem específica) |
| `UUID_PINS` | — | Documento com pins cadastrados |
| `UUID_WEBHOOK_DOCUMENT` | — | Documento para **listar** webhooks |
| `UUID_DOC_WEBHOOK` | — | Documento para **cadastrar** webhook |
| `URL_WEBHOOK` | requestcatcher | URL de callback do webhook |
| `DOCUMENTS_PHASE` | `3` | Fase usada em listagem por status |
| `TEMPLATE_ID_WORD` / `TEMPLATE_ID_HTML` | — | IDs dos templates |
| `HTTP_TIMEOUT` | `30` | Timeout HTTP (segundos) |
| `HTTP_MAX_RETRIES` | `3` | Retries em status retryable |
| `LOG_LEVEL` | `INFO` | Nível do logger |

Pins (`PAGE_*`, `POS_*`, `EXPECTED_PIN_*`) também ficam no `.env` — ver `.env.exemplo`.

### Ambientes D4Sign

| `ENVIRONMENT` | URL base da API |
|---------------|-----------------|
| `prod` | `https://secure.d4sign.com.br/api/v1` |
| `homol` | `https://homol.d4sign.com.br/api/v1` |
| `ghost` | `https://ghost.d4sign.com.br/api/v1` |
| `staging` | `https://stage.d4sign.com.br/api/v1` |
| `hotfix` | `https://hotfix.d4sign.com.br/api/v1` |

### Ambiente efetivo (importante)

O `behave.ini` define `env = hml` (alias de **homol**), que **sobrescreve** o `ENVIRONMENT` do `.env`.

```bash
# Forçar outro ambiente na linha de comando
python -m behave -D env=prod
python -m behave -D env=staging
```

Ou altere `[behave.userdata] env` no `behave.ini`.

Os UUIDs/templates precisam existir **na conta e no ambiente** do token. Valores de outro ambiente geram `Safe not founded`, `File not founded` ou sem permissão no cofre.

## Como executar

### Comandos úteis

```bash
# Suíte completa (18 cenários)
python -m behave features/ -f pretty

# Por tag
python -m behave --tags=@smoke -f pretty
python -m behave --tags=@upload -f pretty
python -m behave --tags=@signature -f pretty
python -m behave --tags=@critical -f pretty
python -m behave --tags=@webhooks -f pretty

# Feature / cenário específico
python -m behave features/documents/uploads.feature -f pretty
python -m behave --name "Listar webhooks" -f pretty

# Dry-run (lista cenários sem chamar a API)
python -m behave features/ --dry-run --format progress

# Relatório HTML + pretty
mkdir reports
python -m behave features/ -f pretty -f html -o reports/behave_report.html

# Allure
python -m behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

## Tags

| Tag | Efeito |
|-----|--------|
| `@api` | Marcação geral da suíte de API |
| `@smoke` | Subconjunto rápido (listagens básicas) |
| `@critical` | Cenários críticos (docs, upload, pins, signers) |
| `@regression` | Regressão ampliada |
| `@upload` | Uploads de documento |
| `@signature` / `@signers` | Fluxos de signatário / envio |
| `@pins` | Pins (criar / listar) |
| `@template` / `@templates` | Geração via template Word/HTML |
| `@webhooks` | Cadastro / listagem de webhook |
| `@documents` / `@safes` | Domínio do recurso |
| `@wip` | Ignorado por padrão (`default_tags = ~@wip` no `behave.ini`) |

## Arquitetura e convenções

### Camadas

```
Feature (Gherkin) → Steps → Service → BaseClient (HTTPX) → API D4Sign
```

| Camada | Responsabilidade |
|--------|------------------|
| Feature | Linguagem de negócio, sem detalhes HTTP |
| Steps | Orquestram services; asserts nos `Então` |
| Services | Endpoints por recurso (`documents`, `safes`…) |
| BaseClient | Headers, retry, timeout, histórico de calls |
| Config / DataFactory | Ambiente, credenciais e payloads |

### Regras

- Gherkin sempre com `# language: pt`
- Sem HTTP direto nos Steps — sempre via `services/`
- Credenciais e UUIDs somente via `.env` / `Config`
- Assertions centralizadas em `recursos/utils/assertions.py`
- Novo fluxo: `features/<domínio>/`, `features/steps/<domínio>/`, `services/<domínio>_service.py`
- `snake_case` → funções · `PascalCase` → classes · `UPPER_CASE` → constantes

## Evidências e relatórios

| Artefato | Onde | Quando |
|----------|------|--------|
| Evidência HTTP (JSON) | `reports/http/` | Fim de cada cenário |
| Report HTML | `reports/behave_report.html` | Com `-f html -o ...` |
| Allure results | `reports/allure-results/` | Formatter Allure |
| Report JSON | `reports/behave.json` | CI |
| Log console | `reports/behave_console.log` | CI |

Nas evidências HTTP: method/url, headers (mascarados), body, status e response. A pasta `reports/` é gerada na execução e não entra no Git.

## CI (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

Triggers: push/PR em `main`/`master`, e `workflow_dispatch` (inputs opcionais de `tags` e `environment`).

Passos principais:

1. Python 3.13
2. `pip install -r requirements.txt`
3. Gera `.env` via `create_env_ci.py` (secrets)
4. Dry-run + execução Behave com `-D env=<environment>` (respeita o input/variável do workflow; não fica preso ao `env=hml` do `behave.ini`)
5. Job Summary + upload do artefato `behave-api-reports`

Secrets típicos: `TOKEN_API`, `CRYPT_KEY`, `EMAIL_TESTE`, `UUID_SAFE`, `LIST_ESPECIFIC_DOCUMENT`, `UUID_PINS`, `UUID_WEBHOOK_DOCUMENT`, `UUID_DOC_WEBHOOK`, `TEMPLATE_ID_WORD`, `TEMPLATE_ID_HTML` (e opcionalmente `USERNAME` / `PASSWORD` / `WHATSAPP_TESTE`).

Variable / input: `ENVIRONMENT` (padrão `homol` no CI).

No disparo manual, o campo **Tags** filtra cenários (`@smoke`, `@critical`, …). Vazio = suíte completa.

## Tempo de execução

| Escopo | Ordem de grandeza |
|--------|-------------------|
| `@smoke` | ~15–40 s |
| Cenário de listagem (GET) | ~2–15 s |
| Uploads / signers / templates | ~5–30 s cada |
| Suíte completa (18) | ~2–3 min (homol; depende de rede e carga da API) |

Timeouts HTTP (`HTTP_TIMEOUT=30`) e retries (`HTTP_MAX_RETRIES=3`) existem porque a API de homol pode responder 5xx pontual ou demorar em listagens grandes.

## Troubleshooting

### `Safe not founded` / `You do not have permission on that safe`

`UUID_SAFE` inválido ou de outro ambiente/conta. Liste cofres (`@safes`) e use um UUID acessível pelo token atual. Confira também se o `behave.ini` não está forçando `homol` enquanto os IDs são de `prod`.

### `File not founded`

`LIST_ESPECIFIC_DOCUMENT`, `UUID_PINS`, `UUID_WEBHOOK_DOCUMENT` ou `UUID_DOC_WEBHOOK` apontam para documento inexistente nesse ambiente. Use um `uuidDoc` real da conta.

### `LIST_ESPECIFIC_DOCUMENT não configurado no .env`

Variável vazia. Preencha com um UUID de documento válido antes de rodar o cenário de listagem específica.

### `pin.position_x: esperado=600, obtido='600'`

A API pode devolver coordenadas como string. O step de listagem de pins normaliza com `int()` — mantenha `EXPECTED_PIN_POSITION_X` numérico no `.env`.

### Ambiente “errado” mesmo com `.env` em `prod`

O userdata `env = hml` do `behave.ini` sobrescreve o `.env`. Use `-D env=prod` ou ajuste o ini.

### Timeout / retry em GET de listagem

Homol pode demorar em contas com muitos documentos. Aumente `HTTP_TIMEOUT` ou rode com tag mais específica (`@smoke`).

## Dados de teste

Arquivos em `data/files/`:

| Arquivo | Uso |
|---------|-----|
| `doc-testes.pdf` | Upload padrão (PDF, base64, hash, anexo, pins, signers) |

## Licença / uso

Projeto interno de automação QA (Auditeste / D4Sign). Credenciais e tokens **não devem ser commitados** — use `.env` (gitignored) e secrets do GitHub Actions.
