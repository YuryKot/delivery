empty_line := ""

default: lock install lint build test

local:
    uv run python3 -m delivery

build:
    docker compose build

test *args:
    @just down
    docker compose run --rm application pytest {{ args }}
    @just down

run:
    @just down
    docker compose up --remove-orphans
    @just down

down:
    docker compose down --remove-orphans

lock:
    uv lock --upgrade

install:
    uv sync --frozen --all-extras --no-install-project

lint:
    -uv run auto-typing-final .
    -uv run ruff check
    -uv run ruff format
    uv run mypy .

revision REVISION="another revision":
    @just down
    docker compose run --rm migrations bash -c 'alembic upgrade head && alembic revision --autogenerate -m "{{ REVISION }}"'

run-web RUN_PARAMS="empty_line":
    @docker compose run "{{ RUN_PARAMS }}" --service-ports application granian --interface asgi articles.application:application --reload --host 127.0.0.1 --port 9991


sh:
    docker compose run --rm application bash
