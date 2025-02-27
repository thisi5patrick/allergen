FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv venv

ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --frozen --no-install-project

COPY . /app

RUN uv sync --frozen

RUN chmod +x /app/scripts/entrypoint.sh

ENTRYPOINT ["/app/scripts/entrypoint.sh"]

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
