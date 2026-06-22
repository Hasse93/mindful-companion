# Mindful Companion 🌿

[![CI](https://github.com/Hasse93/mindful-companion/actions/workflows/ci.yml/badge.svg)](https://github.com/Hasse93/mindful-companion/actions/workflows/ci.yml)

**[🔴 Live demo](https://mindful-wellness-app.vercel.app)** · **[API docs](https://hasse93-mindful-companion-api.hf.space/docs)**

A full-stack **mental-wellness companion** that combines a safety-aligned LLM chat
experience with custom NLP models for mood insight. Built as a software-engineering
portfolio piece.

> **Try it instantly** — log in with the demo account **`demo@mindful.app`** / **`demopass123`**,
> or create your own. (The backend sleeps after inactivity, so the first load may take ~30s to wake.)

> ⚠️ **Not a medical device.** This project is a supportive journaling/wellness tool,
> not therapy, diagnosis, or a crisis service. It always directs users in distress to
> professional crisis resources.

## Highlights

- **Full-stack:** FastAPI (async) backend + Next.js 16 / React 19 frontend, JWT auth with per-user data isolation.
- **Real ML, trained from scratch:** fine-tuned DistilBERT on GoEmotions (**test macro-F1 0.63 / accuracy 0.70**, 7 Ekman emotions), exported to **ONNX** for ~10 ms inference.
- **Safety-first design:** Claude chat behind a non-clinical system prompt + a high-recall crisis-triage layer that surfaces professional resources — never diagnoses.
- **Polished UX:** "Calm Aurora" glassmorphic UI with dark mode, animations, mood tracking, journaling, breathing/grounding tools, and weekly insight reports.
- **Engineering discipline:** 34 backend tests, typed end-to-end, GitHub Actions CI, Docker Compose.

---

## What it does

| Feature | How it works |
|---|---|
| **AI chat support** | Claude (Anthropic) behind a non-clinical safety system prompt, streamed over SSE |
| **Crisis safety triage** | High-recall rule + emotion-signal layer → surfaces 988 / hotlines, never diagnoses |
| **Sentiment analysis** | Pretrained DistilBERT (SST-2) on every note |
| **Emotion classification** | DistilBERT/RoBERTa fine-tuned on **GoEmotions** (7 Ekman emotions) |
| **Mood tracking** | 1–5 check-ins + notes, enriched with the ML pipeline |
| **Weekly reports** | Aggregated mood/emotion/sentiment trends summarised warmly by Claude |

## Tech stack

- **Backend:** FastAPI (async) · SQLModel · PostgreSQL · Anthropic SDK · Hugging Face Transformers
- **ML:** DistilBERT fine-tuned on GoEmotions, exported to ONNX; experiments tracked in MLflow
- **Frontend:** Next.js 15 · TypeScript · Tailwind · shadcn/ui (see `frontend/` — bootstrap below)
- **Infra:** Docker Compose · GitHub Actions CI

## Architecture

```
Next.js (chat · mood calendar · weekly dashboard)
        │  REST + SSE
FastAPI ─┼─ /chat     Claude stream + inline safety triage
        ├─ /analyze  sentiment + emotion + triage pipeline
        ├─ /mood     CRUD, notes enriched by the pipeline
        ├─ /report   weekly aggregation + Claude summary
        └─ /crisis   standalone triage → resources
        │
   ┌────┴─────┐         ┌──────────────┐      ┌────────────┐
 PostgreSQL          HF Transformers       Claude API
                     (sentiment/emotion)   (conversation)
```

---

## Quick start (backend)

The API boots **with no API key and no model downloads** thanks to `FAKE_AI`
stubs — great for a first run and for the test suite.

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env            # optionally add ANTHROPIC_API_KEY

# Run the tests (uses FAKE_AI + in-memory SQLite, no key/models needed):
FAKE_AI=true pytest

# Run the API (needs Postgres — see Docker below):
uvicorn app.main:app --reload
# Docs at http://localhost:8000/docs
```

### With Docker (Postgres + API)

```bash
docker compose up --build
```

### Train your own emotion model (the ML centrepiece)

```bash
cd backend
pip install datasets accelerate "optimum[onnxruntime]" mlflow
# Full run (test macro-F1 0.63 / acc 0.70 on 7 Ekman classes; ~2 hrs on CPU):
python ml_training/train_emotion.py --epochs 3 --output ./models/emotion
# Quick smoke run instead (minutes):
#   python ml_training/train_emotion.py --max-train-samples 1500 --epochs 1 --no-onnx
# Export to ONNX for fast serving (~10 ms/inference):
python ml_training/export_onnx.py --model ./models/emotion --output ./models/emotion-onnx
# then set EMOTION_MODEL=./models/emotion-onnx in .env
```

The backend's `app/ml/emotion.py` auto-detects `model.onnx` in the model dir and
serves it via ONNX Runtime; otherwise it loads the PyTorch model.

---

## Frontend

Next.js 16 (App Router) + React 19 + TypeScript + Tailwind v4, in `frontend/`.

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000 (expects the API on :8000)
```

Views:
- **`/chat`** — streams `POST /chat` over SSE, renders the `triage` event as a
  `CrisisBanner` (resources surfaced immediately for crisis/elevated levels).
- **`/mood`** — emoji check-in + note → `POST /mood`, lists recent entries with
  their detected emotion/sentiment.
- **`/insights`** — `GET /report/weekly`: stat cards, an emotion bar chart, and
  the Claude-written reflection.

The API client lives in `src/lib/api.ts` (types mirror the backend schemas).
`NEXT_PUBLIC_API_URL` is set in `frontend/.env.local`.
TODO: generate the client from the backend OpenAPI spec so types never drift.

---

## Responsible-AI notes

- The companion **never diagnoses** or gives medical/medication advice (enforced in the system prompt).
- Crisis triage is **high-recall by design** — it prefers false alarms (an extra help banner) over misses.
- Crisis resources live in code, not the database, so they can never be empty when needed.
- Mental-health text is sensitive: keep `.env` secret, encrypt at rest in production, and offer data deletion.

## Deployment

The app is structured to deploy as two services:

**Frontend → Vercel**
```bash
cd frontend
vercel --prod      # set NEXT_PUBLIC_API_URL to your backend's public URL
```

**Backend → Render / Railway / Fly.io** (the `backend/Dockerfile` is ready to use)
- Set env vars: `ANTHROPIC_API_KEY`, `DATABASE_URL` (a managed Postgres), `CORS_ORIGINS`
  (your Vercel URL), `JWT_SECRET`, `EMOTION_MODEL=./models/emotion-onnx`.
- For a lean image, serve emotion inference with `onnxruntime` only and drop the
  heavy `torch`/`transformers` training deps from the runtime image.
- Switch `DATABASE_URL` from the local SQLite default to the managed Postgres.

> The repo ships the trained ONNX model under `backend/models/` (gitignored by
> default for size); bake it into the image or pull it from object storage at boot.

## Roadmap

- [x] Phase 0 — Safety framing, crisis triage + tests
- [x] Phase 1 — Streaming Claude chat
- [x] Phase 2 — Sentiment + emotion pipeline, training script
- [x] Phase 3 — Mood tracking
- [x] Phase 4 — Weekly reports
- [x] Phase 5a — Frontend (chat/mood/insights, SSE streaming, crisis banner)
- [x] Phase 5b — Trained the GoEmotions emotion model (**test macro-F1 0.63 / accuracy 0.70**, 7 Ekman classes)
- [x] Phase 5c — ONNX export (~10 ms/inference) + GitHub Actions CI (backend pytest, frontend lint/build)
- [x] Phase 6 — **Calm Aurora redesign**: glassmorphism + aurora-gradient theme, dark mode, Plus Jakarta Sans, Framer Motion animations. New features: dashboard with streaks, breathing + 5-4-3-2-1 grounding tools, journaling + gratitude (`/journal`, ML-enriched), mood calendar heatmap + trend charts, affirmations
- [x] Phase 7 — **JWT auth**: register/login, bcrypt-hashed passwords, Bearer-token enforcement on all data routes, per-user data isolation; frontend login/register gate + logout
- [ ] Phase 8 — git init + push to GitHub (so CI runs), OpenAPI→TS client generation
```
