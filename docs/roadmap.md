# Roadmap Biblioteca Magica

## Status atual (versao em execucao)

### Entregue
- [x] Upload de PDF e criacao de job assincrono.
- [x] Extracao de texto e imagens com PyMuPDF.
- [x] Traducao via LibreTranslate local.
- [x] Deteccao automatica de idioma de origem.
- [x] Geracao de EPUB reflowable.
- [x] Capa automatica com a primeira imagem extraida (quando houver).
- [x] Polling de progresso geral e progresso de traducao.
- [x] Preview de capitulos via API.
- [x] Download do EPUB final.

### Limitacoes conhecidas
- [ ] Jobs em memoria (reiniciar backend limpa historico em execucao).
- [ ] Estrutura de capitulos ainda em modo continuo (chapter-1).
- [ ] Foco em PDFs digitais; OCR para PDF escaneado ainda nao implementado.

## Proxima fase (prioridade alta)

### Fase 2 - Robustez e qualidade de extracao
- [ ] OCR opcional para PDFs escaneados.
- [ ] Heuristica para remover cabecalhos e rodapes repetidos.
- [ ] Melhor associacao entre imagem e legenda.
- [ ] Segmentacao de capitulos mais inteligente (alem de capitulo unico).

### Fase 3 - Qualidade de traducao
- [ ] Glossario customizado por projeto.
- [ ] Cache/memoria de traducao local para blocos repetidos.
- [ ] Revisao opcional de trechos com baixa confianca.

## Evolucao de produto (medio prazo)

### Fase 4 - UX e operacao
- [ ] Tela de historico de jobs com reprocessamento.
- [ ] Preview lado a lado (original x traduzido).
- [ ] Painel de logs por job no frontend.
- [ ] Configuracao de perfil de saida EPUB (tipografia/espacamento).

### Fase 5 - Escalabilidade local
- [ ] Fila interna com concorrencia controlada.
- [ ] Processamento em lote de multiplos PDFs.
- [ ] Limpeza automatica de artefatos antigos.
- [ ] Persistencia de metadados de job (SQLite/PostgreSQL).
