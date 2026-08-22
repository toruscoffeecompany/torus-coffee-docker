FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
RUN apt-get update -qq && apt-get install -y -qq curl >/dev/null 2>&1
COPY --from=builder /install /usr/local
WORKDIR /app
COPY pos_api.py ./
RUN groupadd -r torus && useradd -r -g torus torus && chown -R torus:torus /app
USER torus
EXPOSE 3100
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://127.0.0.1:3100/health || exit 1
CMD ["uvicorn", "pos_api:app", "--host", "0.0.0.0", "--port", "3100"]
