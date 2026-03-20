PYTHON := uv run python

.PHONY: help install run migrate makemigrations shell superuser test test-cov lint format typecheck template-lint template-format check

install:
	uv sync --dev

run:
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate

makemigrations:
	$(PYTHON) manage.py makemigrations

shell:
	$(PYTHON) manage.py shell

superuser:
	$(PYTHON) manage.py createsuperuser

test:
	uv run pytest

test-cov:
	uv run coverage run -m pytest
	uv run coverage report

lint:
	uv run ruff check .
	uv run djlint --check .

format:
	uv run ruff format .
	uv run djlint --reformat .

typecheck:
	uv run mypy .

template-lint:
	uv run djlint --check .

template-format:
	uv run djlint --reformat .

check:
	uv run ruff check .
	uv run djlint --check .
	uv run mypy .
	uv run pytest
