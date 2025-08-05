#!/bin/bash
# Script de lancement Docker simplifié

set -e

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration par défaut
MODEL_ID=${MODEL_ID:-gpt2}
VARIANT=${1:-baseline}
ACTION=${2:-run}

echo -e "${BLUE}🚀 Lancement Docker inference-optim-llm${NC}"
echo -e "Variante: ${GREEN}$VARIANT${NC}"
echo -e "Action: ${GREEN}$ACTION${NC}"
echo -e "Modèle: ${GREEN}$MODEL_ID${NC}"
echo ""

# Fonction d'aide
show_help() {
    echo "Usage: ./docker-run.sh [VARIANT] [ACTION]"
    echo ""
    echo "VARIANT:"
    echo "  baseline    - HuggingFace + PyTorch (défaut)"
    echo "  trtllm      - TensorRT-LLM optimisé"
    echo "  dev         - Mode développement interactif"
    echo "  bench       - Benchmark complet (baseline + trtllm)"
    echo ""
    echo "ACTION:"
    echo "  run         - Exécuter l'inférence (défaut)"
    echo "  build       - Construire les images Docker"
    echo "  shell       - Ouvrir un shell interactif"
    echo "  clean       - Nettoyer les containers et volumes"
    echo ""
    echo "Exemples:"
    echo "  ./docker-run.sh baseline run"
    echo "  ./docker-run.sh trtllm build"
    echo "  ./docker-run.sh bench run"
    echo "  ./docker-run.sh dev shell"
    echo ""
    echo "Variables d'environnement:"
    echo "  MODEL_ID=gpt2 ./docker-run.sh baseline run"
    echo "  CUDA_VISIBLE_DEVICES=0,1 ./docker-run.sh trtllm run"
}

# Vérification Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ docker-compose n'est pas disponible${NC}"
    exit 1
fi

# Fonction pour utiliser docker compose ou docker-compose
docker_compose() {
    if docker compose version &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# Chargement de la configuration
if [ -f .env.docker ]; then
    echo -e "${YELLOW}📋 Chargement configuration .env.docker${NC}"
    export $(cat .env.docker | grep -v '^#' | xargs)
fi

case $ACTION in
    "build")
        echo -e "${BLUE}🔨 Construction des images Docker...${NC}"
        case $VARIANT in
            "baseline")
                docker_compose build baseline
                ;;
            "trtllm")
                docker_compose build trtllm
                ;;
            "bench"|"all")
                docker_compose build baseline trtllm
                ;;
            *)
                echo -e "${RED}❌ Variante inconnue: $VARIANT${NC}"
                show_help
                exit 1
                ;;
        esac
        echo -e "${GREEN}✅ Construction terminée${NC}"
        ;;
        
    "run")
        echo -e "${BLUE}🏃 Exécution $VARIANT...${NC}"
        case $VARIANT in
            "baseline")
                docker_compose --profile baseline up --build
                ;;
            "trtllm")
                docker_compose --profile trtllm up --build
                ;;
            "bench")
                echo -e "${YELLOW}🏁 Benchmark complet (baseline + trtllm + analyse)${NC}"
                docker_compose --profile bench up --build
                ;;
            "dev")
                echo -e "${YELLOW}💻 Mode développement${NC}"
                docker_compose --profile dev up --build
                ;;
            *)
                echo -e "${RED}❌ Variante inconnue: $VARIANT${NC}"
                show_help
                exit 1
                ;;
        esac
        ;;
        
    "shell")
        echo -e "${BLUE}🐚 Ouverture shell interactif...${NC}"
        case $VARIANT in
            "baseline")
                docker_compose run --rm baseline bash
                ;;
            "trtllm")
                docker_compose run --rm trtllm bash
                ;;
            "dev")
                docker_compose --profile dev run --rm dev bash
                ;;
            *)
                echo -e "${RED}❌ Variante inconnue pour shell: $VARIANT${NC}"
                echo "Utilisez: baseline, trtllm, ou dev"
                exit 1
                ;;
        esac
        ;;
        
    "clean")
        echo -e "${YELLOW}🧹 Nettoyage Docker...${NC}"
        docker_compose down --volumes --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Nettoyage terminé${NC}"
        ;;
        
    "help"|"-h"|"--help")
        show_help
        ;;
        
    *)
        echo -e "${RED}❌ Action inconnue: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Terminé !${NC}"