.PHONY: install dev test lint clean docker-build docker-up docker-down

install:
	poetry install

dev:
	poetry install --with dev

test:
	poetry run pytest tests/ -v --cov=shared --cov-report=term-missing

lint:
	poetry run ruff check .
	poetry run mypy shared/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
