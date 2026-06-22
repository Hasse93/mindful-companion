---
title: Mindful Companion API
emoji: 🌿
colorFrom: green
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# Mindful Companion API

FastAPI backend for the Mindful Companion mental-wellness app — JWT auth,
Gemini-powered companion chat with a crisis-safety triage layer, mood &
journaling endpoints, and emotion/sentiment classification served torch-free
via ONNX Runtime (a DistilBERT model fine-tuned on GoEmotions).

This Space runs the Docker image in `Dockerfile`. Configure these as **Space
secrets** (Settings → Variables and secrets):

- `GEMINI_API_KEY` — your Google Gemini API key
- `DATABASE_URL` — a Postgres connection string (e.g. from Neon)
- `CORS_ORIGINS` — your frontend origin (the Vercel URL)
- `JWT_SECRET` — any long random string

Health check: `GET /health`. API docs: `/docs`.
