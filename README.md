# Biblioteca Magica

Projeto local para converter e traduzir PDF para EPUB (reflowable) usando FastAPI no backend e React + Vite no frontend.

## Stack
- Frontend: React, Vite, TypeScript, Axios
- Backend: FastAPI, PyMuPDF, EbookLib, Requests
- Traducao: LibreTranslate local

## Estrutura
- frontend: UI para upload, acompanhamento de status e download
- backend: API de jobs, pipeline PDF -> extracao -> traducao -> EPUB
- docs: roadmap e evolucao do projeto

## Como rodar

### 1. Subir o LibreTranslate
Windows PowerShell:

```powershell
cd backend
.venv\Scripts\python -m pip install libretranslate
.venv\Scripts\libretranslate.exe --host 127.0.0.1 --port 5000 --load-only en,pt
```

Observacao: se preferir, ative a venv antes e rode apenas `libretranslate ...`.

### 2. Rodar o backend
Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Rodar o frontend
Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

## Fluxo atual (MVP)
1. Enviar PDF para POST /jobs
2. Polling em GET /jobs/{job_id}
3. Download do EPUB em GET /jobs/{job_id}/download

## Observacoes
- O projeto esta focado em PDFs com texto digital (nao escaneados).
- Em caso de falha de traducao, o backend preserva texto original no bloco.
- A organizacao de capitulos ainda usa uma estrutura inicial simples (um capitulo principal), com espaco para evolucao.
