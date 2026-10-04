FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
RUN apt-get update -qq && apt-get install -y -qq curl >/dev/null 2>&1
COPY --from=builder /install /usr/local
WORKDIR /app
COPY inventory_api.py inventory_master.json ./
RUN mkdir -p /vault/04_Products && cp inventory_master.json /vault/04_Products/ 2>/dev/null || true
RUN groupadd -r torus && useradd -r -g torus torus && chown -R torus:torus /app
USER torus
EXPOSE 3200
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl -f http://127.0.0.1:3200/health || exit 1
CMD ["uvicorn", "inventory_api:app", "--host", "0.0.0.0", "--port", "3200"]
