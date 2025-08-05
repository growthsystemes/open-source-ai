# 🐳 Guide Docker - Inference Optim LLM

Docker est la **solution recommandée** pour éviter tous les problèmes d'environnement !

## 🚀 Démarrage Rapide (5 minutes)

### 1. Préparation
```bash
# Copiez la configuration
cp env.docker.example .env

# Rendez le script exécutable (Linux/Mac)
chmod +x docker-run.sh
```

### 2. Test Baseline (Sans GPU)
```bash
# Linux/Mac
./docker-run.sh baseline run

# Windows PowerShell
docker-compose --profile baseline up --build
```

### 3. Test Complet avec GPU
```bash
# Linux/Mac
./docker-run.sh bench run

# Windows PowerShell
docker-compose --profile bench up --build
```

## 📋 Commandes Disponibles

### Via Script (Linux/Mac)
```bash
# Construction des images
./docker-run.sh baseline build
./docker-run.sh trtllm build

# Exécution
./docker-run.sh baseline run
./docker-run.sh trtllm run
./docker-run.sh bench run

# Mode développement
./docker-run.sh dev shell

# Nettoyage
./docker-run.sh clean
```

### Via Docker Compose Direct
```bash
# Baseline seulement
docker-compose --profile baseline up --build

# TensorRT-LLM seulement  
docker-compose --profile trtllm up --build

# Benchmark complet
docker-compose --profile bench up --build

# Mode développement
docker-compose --profile dev up --build

# Nettoyage
docker-compose down --volumes
```

## 🔧 Configuration

### Variables d'Environnement (.env)
```bash
MODEL_ID=gpt2                    # Modèle à utiliser
BATCH_SIZE=1                     # Taille de batch
MAX_NEW_TOKENS=32               # Tokens à générer
CUDA_VISIBLE_DEVICES=0          # GPU à utiliser
TRT_PRECISION=fp16              # Précision TensorRT
```

### Modèles Recommandés
```bash
# Test rapide (CPU OK)
MODEL_ID=gpt2

# Production légère
MODEL_ID=microsoft/DialoGPT-small

# Production complète (GPU recommandé)
MODEL_ID=meta-llama/Llama-2-7b-chat-hf
```

## 📊 Résultats

Les résultats sont sauvegardés dans `./reports/` :
- `baseline.jsonl` - Métriques baseline
- `trtllm.jsonl` - Métriques TensorRT-LLM
- `benchmark_results.md` - Rapport comparatif

## 🛠️ Développement

### Mode Interactif
```bash
# Ouvrir un shell dans le conteneur
./docker-run.sh dev shell

# Ou avec docker-compose
docker-compose --profile dev run --rm dev bash
```

### Tests dans le Conteneur
```bash
# Une fois dans le conteneur
python -m inference_optim_llm.cli --help
python -m inference_optim_llm.cli run baseline --max-new-tokens 10
python scripts/validate_setup.py
```

## 🐛 Résolution de Problèmes

### Erreur GPU
```bash
# Vérifiez NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Utilisez CPU seulement
export CUDA_VISIBLE_DEVICES=""
./docker-run.sh baseline run
```

### Problème de Build
```bash
# Nettoyage complet
./docker-run.sh clean
docker system prune -a

# Rebuild from scratch
./docker-run.sh baseline build
```

### Problème Permissions (Linux)
```bash
# Ajustez les permissions
sudo chown -R $USER:$USER ./reports
sudo chown -R $USER:$USER ./engines
```

## 📈 Benchmark Complet

### Lancement
```bash
# Benchmark avec GPU
CUDA_VISIBLE_DEVICES=0 ./docker-run.sh bench run

# Benchmark CPU seulement
CUDA_VISIBLE_DEVICES="" ./docker-run.sh bench run
```

### Analyse des Résultats
```bash
# Voir le rapport
cat reports/benchmark_results.md

# Voir les métriques raw
cat reports/baseline.jsonl
cat reports/trtllm.jsonl
```

## 🎯 Cas d'Usage

### 1. Test Rapide Baseline
```bash
MODEL_ID=gpt2 MAX_NEW_TOKENS=16 ./docker-run.sh baseline run
```

### 2. Benchmark Production
```bash
MODEL_ID=meta-llama/Llama-2-7b-chat-hf ./docker-run.sh bench run
```

### 3. Développement Interactif
```bash
./docker-run.sh dev shell
# Dans le conteneur: modifier le code et tester
```

## ✅ Avantages Docker

- ✅ **Pas de problèmes Python/PyTorch**
- ✅ **Environnement reproductible**
- ✅ **Installation automatique des dépendances**
- ✅ **Isolation complète**
- ✅ **Support GPU automatique**
- ✅ **Cache des modèles persistant**

**🎉 Docker = Solution universelle qui marche partout !**