#!/bin/bash
# Script pour configurer l'authentification NVIDIA NGC

set -e

echo "🔐 Configuration NVIDIA NGC Registry"
echo "================================="

# Vérification Docker
echo "🔍 Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trouvé. Veuillez installer Docker."
    exit 1
fi
echo "✅ Docker trouvé"

# Instructions pour obtenir la clé API
if [ -z "$1" ]; then
    echo ""
    echo "📋 Pour obtenir votre clé API NGC :"
    echo "1. Aller sur https://ngc.nvidia.com"
    echo "2. Créer un compte (gratuit)"
    echo "3. Aller dans Profile > Setup > Generate API Key"
    echo "4. Copier la clé (commence par 'nvapi-')"
    echo ""
    
    # Demander la clé interactivement
    while true; do
        read -p "🔑 Entrez votre clé API NGC: " api_key
        if [ -z "$api_key" ]; then
            echo "❌ Clé API requise"
            continue
        elif [[ ! "$api_key" =~ ^nvapi- ]]; then
            echo "⚠️  La clé API doit commencer par 'nvapi-'"
            read -p "Continuer quand même ? (o/n): " continue_anyway
            if [ "$continue_anyway" = "o" ] || [ "$continue_anyway" = "O" ]; then
                break
            fi
            continue
        else
            break
        fi
    done
else
    api_key="$1"
fi

echo ""
echo "🔑 Connexion au registry NVIDIA..."

# Connexion Docker
echo "$api_key" | docker login nvcr.io --username '$oauthtoken' --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Connexion réussie !"
    
    # Test de l'image TensorRT-LLM
    echo ""
    echo "🧪 Test de l'image TensorRT-LLM..."
    echo "⏳ Téléchargement en cours (peut prendre plusieurs minutes)..."
    
    if docker pull nvcr.io/nvidia/tensorrt_llm:0.7.1-py3; then
        echo "✅ Image TensorRT-LLM téléchargée avec succès !"
        echo ""
        echo "🚀 Vous pouvez maintenant lancer le benchmark :"
        echo "   make all"
        echo "   ou"
        echo "   docker-compose --profile auto up benchmark-full"
    else
        echo "⚠️  Téléchargement de l'image échoué, mais l'authentification a réussi"
        echo "   Essayez de relancer le benchmark, l'image se téléchargera automatiquement"
    fi
else
    echo "❌ Échec de la connexion"
    echo "Vérifiez votre clé API sur https://ngc.nvidia.com"
    exit 1
fi

echo ""
echo "🎯 Configuration terminée !"
