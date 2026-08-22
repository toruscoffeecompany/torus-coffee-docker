FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ─══ Create Hermes bridge directories ────────────────────────────────────────
RUN mkdir -p /data/inbox /data/outbox

# ─══ Create non-root user ─────────────────────────────────────────────────────
RUN useradd -m botuser && chown -R botuser:botuser /app && chown -R botuser:botuser /data

USER botuser

# ─══ Environment ───────────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8765

# ─══ Run bot ───────────────────────────────────────────────────────────────────
CMD ["python", "bot.py"]
