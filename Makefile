.PHONY: help install test lint format security clean run-api run-frontend

help:  ## Show this help message
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

test:  ## Run all tests
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

lint:  ## Run linters (flake8, mypy)
	flake8 . --max-line-length=120 --extend-ignore=E203,W503 --exclude=.venv,venv,__pycache__,.git
	mypy . --config-file=mypy.ini

format:  ## Format code with black and isort
	black . --line-length=120
	isort . --profile=black --line-length=120

security:  ## Run security checks
	bandit -r . -ll --skip=B101 -x .venv,venv,tests

check: lint security test  ## Run all checks (lint + security + test)

clean:  ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

run-api:  ## Run API server
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

run-frontend:  ## Run frontend server
	cd frontend/static_demo && python -m http.server 8001

setup:  ## Complete setup (install + download data + train)
	make install
	python data/data_fetch_and_prepare.py --datasets assistments --seed 42
	python train_dkt.py --epochs 3 --seed 42

validate:  ## Run validation script
	python validar_sistema.py
