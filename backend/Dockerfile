FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Lean, torch-free production deps (ONNX Runtime serving). Cached separately.
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# App code + the exported ONNX models (baked into the image).
COPY app ./app
COPY models ./models

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
