# LEXIS-X5

**Document Intelligence Agentique pour la SST**

> Vos documents SST parlent enfin aux agents IA.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18-61dafb.svg)](https://react.dev)

## Description

LEXIS-X5 permet aux professionnels SST de transformer leurs PDFs (rapports d'inspection, normes CSA, fiches SIMDUT, PV de comités, guides de prévention) en intelligence exploitable par agents IA.

### Pipeline 7 couches

1. **INGEST** — Upload PDF, drag & drop, batch
2. **PARSE** — OpenDataLoader markdown/json structuré
3. **CLASSIFY** — Classification auto type document SST (Claude Sonnet)
4. **EXTRACT** — Entités SST : dangers, EPI, articles LSST/RSST, seuils, secteurs SCIAN
5. **CONNECT** — Liaison 697K records CNESST par secteur SCIAN + Neo4j SafetyGraph
6. **QUERY** — Chat agentic RAG (ChromaDB + Claude)
7. **EXPORT** — Rapports, chunks EDGY, alertes réglementaires, PDF annoté

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 18 + TypeScript + Vite + shadcn/ui + Tailwind |
| Backend | FastAPI (Python 3.12) |
| Parsing | opendataloader-pdf (100% local, CPU only) |
| IA | Claude Sonnet (classification + extraction) |
| DB | Supabase (ca-central-1) |
| Vector | ChromaDB (RAG local) |
| Auth | Supabase magic link OTP |

## Getting started

### Prérequis

- Python 3.12+
- Node.js 20+
- Java 17+ (requis par opendataloader-pdf)

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Conformité

- **Loi 25 Québec** : hébergement ca-central-1, aucune donnée hors Canada
- **Parsing local** : 100% CPU only, zéro appel cloud
- **HITL** : validation humaine sur classifications critiques
- **PROV-O** : traçabilité source via bounding boxes OpenDataLoader

## Écosystème

Fait partie de l'écosystème **AgenticX5 / ReadinessX5 / GenAISafety** par [Preventera](https://github.com/Preventera).

## Licence

[Apache 2.0](LICENSE)
