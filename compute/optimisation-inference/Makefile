# Makefile pour inference-optim-llm
# Usage: make <target>

.PHONY: help install test lint format clean docker-build docker-test quick-start validate

# Configuration
PYTHON := python
PIP := pip
DOCKER_COMPOSE := docker-compose

help: ## Affiche l'aide
	@echo "🚀 Makefile pour inference-optim-llm"
	@echo ""
	@echo "Cibles disponibles :"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# Installation et setup
# =============================================================================

quick-start: ## Setup rapide automatique
	$(PYTHON) quick_start.py

install: ## Installation complète des dépendances
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

install-minimal: ## Installation minimale
	$(PIP) install -e .
	$(PIP) install torch transformers typer rich huggingface-hub

setup-env: ## Crée le fichier .env depuis l'exemple
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Fichier .env créé - éditez-le selon vos besoins"; \
	else \
		echo "✅ Fichier .env déjà présent"; \
	fi

validate: ## Valide l'installation
	$(PYTHON) scripts/validate_setup.py

# =============================================================================
# Développement
# =============================================================================

test: ## Lance les tests
	pytest tests/ -v

test-cov: ## Lance les tests avec coverage
	pytest tests/ --cov=inference_optim_llm --cov-report=html --cov-report=term

lint: ## Vérifie le code avec ruff
	ruff check .

lint-fix: ## Corrige automatiquement le code
	ruff check --fix .

format: ## Formate le code
	ruff format .

type-check: ## Vérification des types avec mypy
	mypy inference_optim_llm/ --ignore-missing-imports

check-all: lint type-check test ## Toutes les vérifications

# =============================================================================
# Utilisation
# =============================================================================

run-baseline: ## Test rapide baseline
	$(PYTHON) -m inference_optim_llm.cli run baseline --max-new-tokens 32

run-help: ## Aide CLI
	$(PYTHON) -m inference_optim_llm.cli --help

bench-quick: ## Benchmark rapide (baseline seulement)
	$(PYTHON) -m inference_optim_llm.cli bench --skip-trtllm --max-new-tokens 32

demo: setup-env run-baseline ## Démo complète (setup + test)

# =============================================================================
# Docker
# =============================================================================

docker-build: ## Build des images Docker
	cd docker && $(DOCKER_COMPOSE) build

docker-test: ## Test Docker baseline
	cd docker && $(DOCKER_COMPOSE) --profile baseline up --abort-on-container-exit

docker-bench: ## Benchmark Docker complet
	cd docker && $(DOCKER_COMPOSE) --profile bench up --abort-on-container-exit

docker-dev: ## Mode développement Docker
	cd docker && $(DOCKER_COMPOSE) --profile dev up

docker-clean: ## Nettoyage Docker
	cd docker && $(DOCKER_COMPOSE) down --volumes --remove-orphans
	docker system prune -f

# =============================================================================
# Analyse et rapports
# =============================================================================

analyze: ## Analyse les résultats de benchmark
	$(PYTHON) scripts/benchmark.py --reports-dir reports/

generate-charts: ## Génère les graphiques
	$(PYTHON) scripts/export_results.py --reports-dir reports/

report: analyze generate-charts ## Rapport complet avec graphiques

# =============================================================================
# Maintenance
# =============================================================================

clean: ## Nettoyage des fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

clean-cache: ## Nettoyage des caches
	rm -rf ~/.cache/huggingface/transformers/
	rm -rf engines/*.engine

upgrade-deps: ## Met à jour les dépendances
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements-dev.txt

# =============================================================================
# CI/CD simulation
# =============================================================================

ci-local: ## Simulation CI en local
	@echo "🔍 Simulation pipeline CI..."
	make lint
	make type-check
	make test
	@echo "✅ CI simulation terminée"

pre-commit: format lint-fix test ## Hook pre-commit

# =============================================================================
# Informations
# =============================================================================

info: ## Informations sur l'environnement
	@echo "📊 Informations environnement:"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "GPU: $$(python -c 'import torch; print(f\"CUDA: {torch.cuda.is_available()}\")')"
	@echo "Package: $$($(PIP) show inference-optim-llm | grep Version || echo 'Non installé')"

# =============================================================================
# Cibles par défaut
# =============================================================================

all: install setup-env validate ## Installation complète