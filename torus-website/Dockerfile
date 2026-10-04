# Stage 1: install deps + build Next.js
FROM node:20-alpine AS builder
WORKDIR /build
COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./
RUN npm install --omit=dev || npm install
COPY . .
RUN npm run build

# Stage 2: serve with nginx
FROM nginx:alpine
RUN apk add --no-cache wget
COPY --from=builder /build/out /usr/share/nginx/html
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/healthz || exit 1
CMD ["nginx", "-g", "daemon off;"]
