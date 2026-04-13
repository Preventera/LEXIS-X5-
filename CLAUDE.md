# CLAUDE.md — LEXIS-X5

PROJET : LEXIS-X5 — Document Intelligence Agentique pour la SST
REPO : Preventera/LEXIS-X5-
AUTEUR : Mario Deshaies — VP AI / CTO, AgenticX5
ÉCOSYSTÈME : AgenticX5 / ReadinessX5 / GenAISafety

## VISION

Application web permettant aux professionnels SST de transformer leurs PDFs
(rapports inspection, normes CSA, fiches SIMDUT, PV comités, guides prévention)
en intelligence exploitable par agents IA.

Tagline : "Vos documents SST parlent enfin aux agents IA."

## ARCHITECTURE

- Frontend : React 18 + TypeScript + Vite + shadcn/ui + Tailwind
- Backend : FastAPI (Python 3.12)
- Parsing : opendataloader-pdf (via sous-module docparse de scrapling-x5)
- IA : Claude Sonnet (classification + extraction entités SST)
- DB : Supabase (ca-central-1, Loi 25 conforme)
- Vector : ChromaDB (RAG local)
- Auth : Supabase magic link OTP

## PIPELINE 7 COUCHES

1. INGEST — Upload PDF, drag & drop, batch
2. PARSE — OpenDataLoader markdown/json structuré
3. CLASSIFY — Classification auto type document SST (Claude Sonnet)
4. EXTRACT — Entités SST : dangers, EPI, articles LSST/RSST, seuils, secteurs SCIAN
5. CONNECT — Liaison 697K records CNESST par secteur SCIAN + Neo4j SafetyGraph
6. QUERY — Chat agentic RAG (ChromaDB + Claude)
7. EXPORT — Rapports, chunks EDGY, alertes réglementaires, PDF annoté

## CONFORMITÉ

- Loi 25 Québec : hébergement ca-central-1, aucune donnée hors Canada
- 100% local pour le parsing (CPU only, pas de cloud)
- HITL : validation humaine sur classifications critiques
- PROV-O : traçabilité source via bounding boxes OpenDataLoader

## MODÈLE COMMERCIAL

- Freemium : 5 PDFs/mois gratuit (individuel)
- Pro : illimité (29$/mois)
- Enterprise : API + intégration EDGY + SSO (sur devis)

## CONVENTIONS

- Une étape à la fois avec point d'arrêt
- Nom de code et localisation déclarés avant chaque fichier
- Pas de code sans OK explicite
- Docstrings FR, type hints complets
- Commits conventionnels : feat(), fix(), docs()

## PRIORITÉS ACTUELLES

- Phase 1 : Scaffold + Upload + Parse (MVP)
- Phase 2 : Classification IA + Extraction entités
- Phase 3 : RAG Chat + Export

## DÉPENDANCES CLÉS

- opendataloader-pdf>=0.9.0
- fastapi>=0.115.0
- supabase-py>=2.0.0
- anthropic>=0.40.0
- chromadb>=0.5.0
- httpx>=0.27.0
- structlog>=24.0
