# Smart Notes AI

Aplicação full-stack de notas inteligentes: você cola um texto ou envia um
arquivo (PDF ou áudio), e a IA gera um resumo automaticamente — tudo rodando
localmente, sem depender de nenhuma API paga.

## Stack

- **Frontend**: Angular 22 (standalone components) + Angular Material
- **Backend**: Python + FastAPI
- **Banco de dados**: PostgreSQL (via Docker Compose)
- **IA local** (sem custo, sem API externa):
  - `faster-whisper` para transcrição de áudio
  - `transformers` + `torch` (CPU) para resumo de texto
- **Autenticação**: JWT (feito à mão com `pyjwt` + `bcrypt`)
- **Processamento assíncrono**: fila em memória (`queue.Queue` + thread única)
  — toda nota é processada em background, nunca bloqueando a requisição HTTP.
  O frontend faz polling do status até `completed`/`failed`.

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (para o Postgres)
- Python 3.11+ (testado com 3.14)
- Node.js 20+ e [Angular CLI](https://angular.dev/tools/cli) (`npm install -g @angular/cli`)

## Como rodar

### 1. Banco de dados

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows (no Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        # ajuste JWT_SECRET_KEY se quiser
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Na primeira execução, os modelos de IA (Whisper + modelo de resumo) são
baixados automaticamente do Hugging Face (~1GB no total) — isso demora um
pouco só na primeira vez.

A documentação interativa da API fica em `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
ng serve
```

Acesse `http://localhost:4200`, crie uma conta e comece a criar notas.

## Testes

```bash
cd backend
pytest
```

Os testes usam um banco `smart_notes_test` separado (criado automaticamente)
e não dependem dos modelos de IA — os serviços de IA são mockados para os
testes rodarem em segundos.

## Simplificações conscientes (para o escopo de portfólio)

- **JWT em `localStorage`** no frontend, em vez de cookie `httpOnly` — mais
  simples de implementar, com o trade-off de exposição a XSS documentado
  aqui de propósito.
- **Modelo de resumo em inglês** (`sshleifer/distilbart-cnn-12-6`) — a
  qualidade do resumo de textos em português é mais limitada. Trocar por um
  modelo multilíngue é uma evolução natural.
- **Fila em memória** (não sobrevive a um restart do processo) em vez de
  Celery+Redis — suficiente para uma aplicação local de portfólio; se o
  processo cair no meio do processamento de uma nota, ela fica presa em
  `processing` (não implementamos retomada automática).
