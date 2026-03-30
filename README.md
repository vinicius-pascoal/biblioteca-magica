# Biblioteca Magica

Projeto local para converter e traduzir PDF para EPUB (reflowable) usando FastAPI no backend e React + Vite no frontend.

## Demo

![Demo do sistema](demo.png)

## Stack
- Frontend: React, Vite, TypeScript, Axios
- Backend: FastAPI, PyMuPDF, EbookLib, Requests, Langdetect
- Traducao: LibreTranslate local

## Pre-requisitos
- Python 3.11+
- Node.js 18+
- npm 9+

## Estrutura
- frontend: UI 8-bit magica para upload, progresso, preview e download
- backend: API de jobs e pipeline PDF -> extracao -> traducao -> EPUB
- docs: roadmap e evolucao do projeto

## Funcionalidades atuais
- Upload de PDF e criacao de job assincrono.
- Polling de status com progresso geral e progresso detalhado da traducao.
- Deteccao automatica de idioma de origem.
- Extracao de texto e imagens com PyMuPDF.
- Geracao de EPUB com:
	- texto traduzido em formato reflowable;
	- imagens incorporadas;
	- capa automatica usando a primeira imagem extraida (quando existir).
- Preview de capitulos via API (com trecho inicial/excerpt).
- Download do EPUB final quando o job conclui.

## Fluxo de interface atual
1. Estado inicial: mostra upload.
2. Durante processamento: upload some e aparece apenas o Job Progress.
3. Ao concluir: aparecem apenas Preview de Capitulos e card de download.
4. Em falha: upload volta a aparecer com mensagem de erro para novo envio.

## Endpoints da API
- `GET /health`: health check.
- `POST /jobs`: cria job a partir de um PDF.
- `GET /jobs/{job_id}`: status e progresso do job.
- `POST /jobs/{job_id}/cancel`: solicita cancelamento de job em andamento.
- `GET /jobs/{job_id}/chapters`: preview de capitulos extraidos/traduzidos.
- `GET /jobs/{job_id}/download`: download do EPUB pronto.

## Como rodar

### Opcao rapida: Docker Compose (tudo com um comando)

Pre-requisito: Docker Desktop (ou Docker Engine + Compose plugin) instalado.

Na raiz do projeto:

```bash
docker compose up --build
```

Para parar:

```bash
docker compose down
```

Servicos disponiveis:
- Frontend: http://127.0.0.1:5173
- Backend: http://127.0.0.1:8000
- LibreTranslate: http://127.0.0.1:5000

Observacoes do Compose:
- O backend usa o endpoint interno `http://libretranslate:5000/translate`.
- A pasta `backend/storage` fica montada como volume para manter os arquivos gerados.
- O frontend usa `VITE_API_BASE_URL=http://127.0.0.1:8000`.
- Limpeza automatica de jobs/arquivos antigos via TTL:
	- `JOB_TTL_HOURS` (padrao: `24`)
	- `CLEANUP_INTERVAL_MINUTES` (padrao: `15`)

### 1. Subir o backend
Windows PowerShell:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Se ainda nao existir venv:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Subir o LibreTranslate
Em outro terminal (tambem dentro de backend):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python -m pip install libretranslate
.\.venv\Scripts\libretranslate.exe --host 127.0.0.1 --port 5000 --load-only en,pt
```

Observacao: se preferir, ative a venv antes e rode apenas `libretranslate ...`.

### 3. Rodar o frontend
Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://127.0.0.1:5173
Backend: http://127.0.0.1:8000
LibreTranslate: http://127.0.0.1:5000

## Observacoes
- O projeto esta focado em PDFs com texto digital (nao escaneados).
- Em caso de falha de traducao de um bloco, o backend preserva o texto original.
- Cancelamento de job e cooperativo: o status muda para `canceled` e os artefatos temporarios do job sao removidos.
- Jobs finalizados e artefatos antigos sao removidos automaticamente conforme TTL configurado.
- A estrutura atual de saida organiza conteudo em capitulo continuo (chapter-1), com preview disponivel via endpoint de capitulos.
- Jobs sao mantidos em memoria no backend (reiniciar API limpa historico em execucao).
- O idioma de destino padrao atual e `pt` (configuravel em `backend/app/core/config.py`).
