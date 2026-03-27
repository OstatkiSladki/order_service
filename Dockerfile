FROM python:3.13-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 
ENV UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY schemas/README.md schemas/README.md
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-trixie

RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/ /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
