FROM python:3.12-alpine

RUN apk add --no-cache git docker-cli

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml ./
COPY src/ src/

RUN uv pip install --system -e .

CMD ["seeder"]
