# Mindful Companion 🌿

[![CI](https://github.com/Hasse93/mindful-companion/actions/workflows/ci.yml/badge.svg)](https://github.com/Hasse93/mindful-companion/actions/workflows/ci.yml)

**[🔴 Live demo](https://mindful-wellness-app.vercel.app)** · **[API docs](https://hasse93-mindful-companion-api.hf.space/docs)**

A full-stack **mental-wellness companion** that pairs a safety-aligned LLM chat
experience with a custom NLP model for mood insight. Built as a software-engineering
portfolio piece.

> **Try it instantly** — log in with the read-only demo account **`demo@mindful.app`** / **`demopass123`**,
> or create your own to save entries. (The backend sleeps after inactivity, so the first load may take ~30s to wake.)

> ⚠️ **Not a medical device.** This is a supportive journaling/wellness tool — not therapy,
> diagnosis, or a crisis service. It always directs users in distress to professional resources.

## Highlights

- **Full-stack, deployed:** FastAPI backend on Hugging Face Spaces · Next.js frontend on Vercel · Neon Postgres.
- **Real ML, trained from scratch:** DistilBERT fine-tuned on **GoEmotions** (test **macro-F1 0.63 / accuracy 0.70**, 7 Ekman emotions), **INT8-quantized** and served **torch-free via ONNX Runtime** (~10 ms inference).
- **Safety-first design:** LLM chat behind a non-clinical system prompt + a high-recall crisis-triage layer that surfaces professional resources — never diagnoses.
- **Polished UX:** "Calm Aurora" glassmorphic UI with dark mode and animations — chat, mood tracking + calendar/trends, journaling, breathing/grounding tools, streaks, weekly insights.
- **Engineering discipline:** JWT auth with per-user isolation, a read-only demo account, **35 backend tests**, GitHub Actions CI.

---

## What it does

| Feature | How it works |
|---|---|
| **AI chat support** | **Google Gemini** (`gemini-2.5-flash`, swappable with Claude) behind a non-clinical safety prompt, streamed over SSE |
| **Crisis safety triage** | High-recall rule + emotion-signal layer → surfaces 988 / hotlines, never diagnoses |
| **Emotion classification** | DistilBERT fine-tuned on **GoEmotions** (7 Ekman emotions), ONNX-served |
| **Sentiment analysis** | DistilBERT (SST-2), ONNX-served |
| **Mood tracking** | 1–5 check-ins + notes, enriched by the ML pipeline; calendar heatmap + trend chart |
| **Journal & gratitude** | Prompted entries, ML-tagged with the detected emotion |
| **Weekly reports** | Aggregated mood/emotion/sentiment trends, summarised warmly by Gemini |

## Tech stack

- **Backend:** FastAPI · SQLModel · PostgreSQL (Neon) · `google-genai` (Gemini) · ONNX Runtime · JWT (PyJWT + bcrypt)
- **ML:** DistilBERT fine-tuned on GoEmotions, INT8-quantized to ONNX; experiments tracked in MLflow
- **Frontend:** Next.js 16 · React 19 · TypeScript · Tailwind v4 · Framer Motion · Recharts · lucide-react
- **Infra:** Docker · GitHub Actions CI · Hugging Face Spaces (backend) · Vercel (frontend)

## Architecture

```
Next.js (chat · dashboard · mood calendar · journal · tools)   ── Vercel
        │  REST + SSE  (JWT Bearer)
FastAPI ─┼─ /auth     register / login (bcrypt + JWT)            ── HF Spaces
        ├─ /chat     Gemini stream + inline safety triage
        ├─ /analyze  sentiment + emotion + triage pipeline
        ├─ /mood     check-ins, notes enriched by the pipeline
        ├─ /journal  journal + gratitude entries
        ├─ /report   weekly aggregation + Gemini summary
        └─ /crisis   standalone triage → resources
        │
   ┌────┴─────┐        ┌────────────────────┐     ┌────────────┐
 Neon Postgres      ONNX Runtime              Gemini API
                    (emotion + sentiment)     (conversation)
```

---

## Quick start (local)

The API boots **with no API key and no model downloads** thanks to `FAKE_AI` stubs.

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt

# Run the tests (FAKE_AI + in-memory SQLite — no key/models needed):
FAKE_AI=true pytest

# Run the API for real (uses the committed ONNX models + local SQLite):
cp .env.example .env        # add your GEMINI_API_KEY for real chat
uvicorn app.main:app --reload
# Docs at http://localhost:8000/docs
```

Frontend:

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000 (expects the API on :8000)
```

The trained, quantized ONNX models ship in `backend/models/` (~64 MB each), so emotion
and sentiment work out of the box with no downloads. Chat falls back to canned replies
until you set a `GEMINI_API_KEY` (free tier).

## Re-training the emotion model (optional)

```bash
cd backend
pip install datasets accelerate "optimum[onnxruntime]" mlflow
python ml_training/train_emotion.py --epochs 3 --output ./models/emotion   # ~2 hrs on CPU
python ml_training/export_onnx.py   --model ./models/emotion --output ./models/emotion-onnx
python ml_training/quantize_onnx.py --dir ./models/emotion-onnx            # 268 MB → 64 MB
```

`app/ml/emotion.py` auto-detects `model.onnx` in the model dir and serves it via ONNX
Runtime; otherwise it falls back to a Transformers (PyTorch) pipeline.

---

## Deployment

Live on free tiers, no credit card:

- **Backend → Hugging Face Spaces (Docker).** The lean image (`backend/Dockerfile`, built on
  `requirements-prod.txt`, torch-free) bakes in the quantized ONNX models. Set Space secrets:
  `GEMINI_API_KEY`, `DATABASE_URL` (Neon), and variables `LLM_PROVIDER`, `EMOTION_MODEL`,
  `SENTIMENT_MODEL`, `CORS_ORIGIN_REGEX`, `JWT_SECRET`.
- **Frontend → Vercel.** Root directory `frontend`; `NEXT_PUBLIC_API_URL` points at the Space
  (baked into `frontend/.env.production`).
- **Database → Neon** (serverless Postgres). The backend auto-rewrites `postgres://` URLs to
  the psycopg3 driver.

A `render.yaml` blueprint is also included for Render.

## Responsible-AI notes

- The companion **never diagnoses** or gives medical advice (enforced in the system prompt).
- Crisis triage is **high-recall by design** — it prefers false alarms (an extra help banner) over misses.
- Crisis resources live in code, not the database, so they can never be empty when needed.
- The Gemini backend uses relaxed safety thresholds **on purpose** so it can respond with care to
  distress rather than refusing; the independent triage layer surfaces professional resources.

## Status

Complete and deployed. Backend, frontend, trained+quantized ML model, Gemini chat, JWT auth,
read-only demo, persistent Neon DB, and green CI are all live.
