# Makefile pour TensorRT-LLM Benchmark
.PHONY: help build all pytorch tensorrt compare clean interactive setup

# Couleurs pour l'affichage
GREEN=\033[0;32m
YELLOW=\033[1;33m
CYAN=\033[0;36m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Affiche cette aide
	@echo "$(GREEN)🚀 TensorRT-LLM Benchmark - Commandes disponibles:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(CYAN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Vérifie l'environnement et crée les répertoires
	@echo "$(YELLOW)🔍 Vérification de l'environnement...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)❌ Docker requis$(NC)"; exit 1; }
	@command -v nvidia-smi >/dev/null 2>&1 || { echo "$(RED)❌ nvidia-smi requis$(NC)"; exit 1; }
	@docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi >/dev/null 2>&1 || { echo "$(RED)❌ Docker GPU support requis$(NC)"; exit 1; }
	@mkdir -p data/{models,engines,checkpoints,results}
	@echo "$(GREEN)✅ Environnement prêt!$(NC)"

build: setup ## Construit le moteur TensorRT-LLM
	@echo "$(CYAN)🔧 Construction du moteur TensorRT...$(NC)"
	docker-compose --profile build-only up build-engine

pytorch: setup ## Exécute le benchmark PyTorch
	@echo "$(CYAN)🔥 Benchmark PyTorch...$(NC)"
	docker-compose --profile pytorch-only up benchmark-pytorch

tensorrt: setup ## Exécute le benchmark TensorRT-LLM
	@echo "$(CYAN)⚡ Benchmark TensorRT...$(NC)"
	docker-compose --profile tensorrt-only up benchmark-tensorrt

compare: ## Compare les résultats
	@echo "$(CYAN)📊 Comparaison des résultats...$(NC)"
	docker-compose --profile compare-only up compare-results

all: setup build pytorch tensorrt compare ## Exécute le pipeline complet
	@echo "$(GREEN)✅ Pipeline complet terminé!$(NC)"
	@echo "$(CYAN)📊 Résultats disponibles dans ./data/results/$(NC)"

auto: setup ## Exécute le benchmark automatique (tout en une fois)
	@echo "$(CYAN)🔄 Benchmark automatique...$(NC)"
	docker-compose --profile auto up benchmark-full

interactive: setup ## Lance un shell interactif dans le container
	@echo "$(CYAN)🖥️  Mode interactif...$(NC)"
	docker-compose --profile manual run --rm tensorrt-llm-benchmark

clean: ## Nettoie les données et containers
	@echo "$(YELLOW)🧹 Nettoyage...$(NC)"
	docker-compose down --volumes --remove-orphans
	rm -rf data/
	docker system prune -f

clean-docker: ## Nettoie les images Docker
	@echo "$(YELLOW)🧹 Nettoyage des images Docker...$(NC)"
	docker-compose down --rmi all --volumes --remove-orphans

results: ## Affiche un résumé des résultats
	@echo "$(CYAN)📊 Résumé des résultats:$(NC)"
	@if [ -f data/results/benchmark_comparison_report.json ]; then \
		echo "$(GREEN)✅ Rapport de comparaison trouvé$(NC)"; \
		echo ""; \
		cat data/results/benchmark_comparison_report.json | jq -r '.speedup_analysis | to_entries[] | "\(.key): \(.value)"' 2>/dev/null || echo "Installez jq pour un affichage formaté"; \
	else \
		echo "$(RED)❌ Aucun rapport trouvé. Exécutez 'make all' d'abord.$(NC)"; \
	fi

logs: ## Affiche les logs du dernier run
	docker-compose logs --tail=50

status: ## Vérifie le statut des containers
	@echo "$(CYAN)📈 Statut des containers:$(NC)"
	docker-compose ps

# Commandes de développement
dev-build: ## Reconstruction de l'image Docker (pour développement)
	docker-compose build --no-cache tensorrt-llm-benchmark

dev-shell: ## Shell de développement avec volumes montés
	docker-compose --profile manual run --rm -v $(PWD)/scripts:/workspace/scripts tensorrt-llm-benchmark bash

# Aliases populaires
benchmark: all ## Alias pour 'all'
run: auto ## Alias pour 'auto'
test: pytorch ## Alias pour 'pytorch' (test rapide)
