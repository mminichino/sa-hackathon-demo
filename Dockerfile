FROM ghcr.io/astral-sh/uv:python3.10-bookworm

WORKDIR /app

COPY . .

RUN uv sync --frozen --no-dev
