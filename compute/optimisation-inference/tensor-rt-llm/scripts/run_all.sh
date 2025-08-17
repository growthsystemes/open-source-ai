#!/bin/bash
set -e

# Script principal pour exécuter tout le pipeline de benchmark
echo "🚀 Démarrage du pipeline complet de benchmark TensorRT-LLM"
echo "=============================================================="

# Vérification de l'environnement
echo "🔍 Vérification de l'environnement..."

if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi non trouvé. Vérifiez l'installation des drivers NVIDIA."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trouvé. Veuillez installer Docker."
    exit 1
fi

# Test de l'accès GPU
echo "🔧 Test de l'accès GPU..."
if ! nvidia-smi > /dev/null 2>&1; then
    echo "❌ Impossible d'accéder au GPU. Vérifiez les drivers NVIDIA."
    exit 1
fi

# Création des répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p data/{models,engines,checkpoints,results}

echo "✅ Environnement vérifié!"
echo ""

# Étape 1: Construction de l'image Docker
echo "1️⃣  Construction de l'image Docker..."
if ! docker-compose build tensorrt-llm-benchmark; then
    echo "❌ Erreur lors de la construction de l'image Docker"
    exit 1
fi

# Étape 2: Construction du moteur TensorRT
echo ""
echo "2️⃣  Construction du moteur TensorRT-LLM..."
if ! docker-compose --profile build-only up build-engine; then
    echo "❌ Erreur lors de la construction du moteur"
    exit 1
fi

# Étape 3: Benchmark PyTorch
echo ""
echo "3️⃣  Benchmark PyTorch (référence)..."
if ! docker-compose --profile pytorch-only up benchmark-pytorch; then
    echo "❌ Erreur lors du benchmark PyTorch"
    exit 1
fi

# Étape 4: Benchmark TensorRT
echo ""
echo "4️⃣  Benchmark TensorRT-LLM..."
if ! docker-compose --profile tensorrt-only up benchmark-tensorrt; then
    echo "❌ Erreur lors du benchmark TensorRT"
    exit 1
fi

# Étape 5: Comparaison
echo ""
echo "5️⃣  Comparaison et analyse des résultats..."
if ! docker-compose --profile compare-only up compare-results; then
    echo "❌ Erreur lors de la comparaison"
    exit 1
fi

# Résultats
echo ""
echo "✅ PIPELINE TERMINÉ!"
echo "===================="
echo "📊 Résultats disponibles dans ./data/results/"
echo "   - pytorch_benchmark.json"
echo "   - tensorrt_benchmark.json" 
echo "   - benchmark_comparison_report.json"
echo "   - benchmark_comparison.png"
echo ""
echo "🔍 Pour voir le résumé:"
echo "   cat ./data/results/benchmark_comparison_report.json | jq '.speedup_analysis'"
echo ""
echo "🎯 Benchmark TensorRT-LLM terminé avec succès!"
