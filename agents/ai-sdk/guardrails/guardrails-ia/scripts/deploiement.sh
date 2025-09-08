#!/bin/bash
# Script de déploiement pour Guardrails IA
# Automatise le build et le lancement de l'application

set -e  # Arrêt du script en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
print_message() {
    echo -e "${2}${1}${NC}"
}

# Configuration par défaut
PROJECT_NAME="guardrails-ia"
DOCKER_IMAGE="${PROJECT_NAME}:latest"
HOST_PORT="${HOST_PORT:-3001}"

print_message "🚀 Démarrage du déploiement Guardrails IA" $BLUE

# Vérification de la présence de Docker
if ! command -v docker &> /dev/null; then
    print_message "❌ Erreur: Docker n'est pas installé ou accessible" $RED
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_message "❌ Erreur: Docker Compose n'est pas installé ou accessible" $RED
    exit 1
fi

# Fonction de nettoyage
cleanup() {
    print_message "🧹 Nettoyage des ressources..." $YELLOW
    docker-compose down 2>/dev/null || true
}

# Piège pour nettoyer en cas d'interruption
trap cleanup EXIT

# Vérification de l'environnement
if [[ -f .env ]]; then
    print_message "📋 Chargement des variables d'environnement depuis .env" $BLUE
    set -a
    source .env
    set +a
else
    print_message "⚠️  Aucun fichier .env trouvé, utilisation des valeurs par défaut" $YELLOW
fi

# Construction de l'image Docker
print_message "🔨 Construction de l'image Docker..." $BLUE
if docker-compose build --no-cache; then
    print_message "✅ Image construite avec succès" $GREEN
else
    print_message "❌ Échec de la construction de l'image" $RED
    exit 1
fi

# Arrêt des conteneurs existants
print_message "🛑 Arrêt des conteneurs existants..." $YELLOW
docker-compose down --remove-orphans

# Démarrage des services
print_message "▶️  Démarrage des services..." $BLUE
if docker-compose up -d; then
    print_message "✅ Services démarrés avec succès" $GREEN
else
    print_message "❌ Échec du démarrage des services" $RED
    exit 1
fi

# Attente que l'application soit prête
print_message "⏳ Attente du démarrage de l'application..." $YELLOW
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if curl -s http://localhost:${HOST_PORT}/health >/dev/null 2>&1; then
        break
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""

if [ $counter -ge $timeout ]; then
    print_message "❌ Timeout: L'application n'a pas démarré dans les temps" $RED
    docker-compose logs
    exit 1
fi

# Vérification finale
print_message "🔍 Vérification de l'état des services..." $BLUE
docker-compose ps

print_message "✅ Déploiement terminé avec succès!" $GREEN
print_message "🌐 Application accessible sur: http://localhost:${HOST_PORT}" $BLUE
print_message "📊 Logs en temps réel: docker-compose logs -f" $BLUE
print_message "🛑 Arrêter l'application: docker-compose down" $BLUE

# Affichage des informations de monitoring (si activé)
if docker-compose --profile monitoring ps monitoring &>/dev/null; then
    print_message "📈 Monitoring disponible sur: http://localhost:${MONITORING_PORT:-9100}" $BLUE
fi

print_message "🎉 Guardrails IA est maintenant opérationnel!" $GREEN