# 🚀 Guide de Setup - Inference Optim LLM

Ce guide vous accompagne étape par étape pour configurer et utiliser le projet.

## 🪟 **UTILISATEURS WINDOWS** → [README_WINDOWS.md](README_WINDOWS.md)

**Problème PyTorch ?** → [CORRECTION_URGENTE.md](CORRECTION_URGENTE.md)

## 📋 Prérequis

- **Python 3.9+** (testé avec 3.9, 3.10, 3.11)
- **GPU NVIDIA** avec CUDA 11.8+ (optionnel pour baseline)
- **8GB+ RAM** (16GB+ recommandé)
- **20GB+ espace disque** (pour les modèles)

## ⚡ Installation Rapide

### 1. Clone et Navigation
```bash
cd inference-optim-LLM
```

### 2. Installation Automatique selon OS
```bash
# Détection automatique Windows/Linux/Mac
python quick_start.py

# Alternative: installation manuelle
python setup_dev.py
```

### 3. Validation
```bash
# Test rapide
python quick_test_windows.py  # Windows
python scripts/validate_setup.py  # Tous OS
```

## 🔧 Installation Manuelle

### 1. Environnement Python
```bash
# Avec conda (recommandé)
conda create -n optim-llm python=3.10
conda activate optim-llm

# Ou avec venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Installation des Dépendances
```bash
# Installation complète
pip install -r requirements-dev.txt

# Ou installation minimale
pip install -e .
pip install torch transformers typer rich huggingface-hub
```

### 3. Configuration
```bash
# Copiez le fichier d'exemple
cp .env.example .env

# Éditez selon vos besoins
nano .env  # ou votre éditeur préféré
```

## 🧪 Tests de Validation

### Test CLI
```bash
# Aide générale
iol --help
python -m inference_optim_llm.cli --help

# Aide commandes spécifiques
iol run --help
iol bench --help
```

### Test Baseline Simple
```bash
# Test avec modèle léger (pour validation)
MODEL_ID=gpt2 iol run baseline --max-new-tokens 10
```

### Test Complet (avec GPU)
```bash
# Benchmark complet
iol bench --batch-size 1 --max-new-tokens 64
```

## 🐳 Utilisation Docker

### Setup Docker
```bash
cd docker

# Build des images
docker-compose build

# Test baseline
docker-compose --profile baseline up

# Benchmark complet
docker-compose --profile bench up
```

### Développement Docker
```bash
# Mode développement interactif
docker-compose --profile dev up
docker-compose exec dev bash
```

## 📊 Premiers Pas

### 1. Test Baseline
```bash
# Test rapide avec un petit modèle
iol run baseline --prompts-file data/prompts.txt --max-new-tokens 32

# Sauvegarde des résultats
iol run baseline --save-json reports/test.jsonl
```

### 2. Benchmark Complet
```bash
# Benchmark baseline vs TensorRT-LLM
iol bench --prompts-file data/prompts.txt --output-dir reports/

# Génération des graphiques
python scripts/export_results.py --reports-dir reports/
```

### 3. Analyse des Résultats
```bash
# Analyse automatique
python scripts/benchmark.py --reports-dir reports/

# Vérification des fichiers générés
ls reports/
# → baseline.jsonl, trtllm.jsonl, benchmark_results.md
```

## 🔧 Configuration Avancée

### Variables d'Environnement (.env)
```bash
# Modèle à utiliser
MODEL_ID=meta-llama/Llama-2-7b-chat-hf

# Configuration GPU
CUDA_VISIBLE_DEVICES=0
TRT_PRECISION=fp16

# Performance
BATCH_SIZE=1
MAX_NEW_TOKENS=64

# Cache
HF_HOME=/path/to/cache
```

### Configuration Multi-GPU
```bash
# Dans .env
CUDA_VISIBLE_DEVICES=0,1
DEVICE_MAP=balanced_low_0

# Ou en ligne de commande
iol run baseline --device-map balanced_low_0
```

## 🚨 Résolution de Problèmes

### Erreur d'Import
```bash
# Réinstallez le package
pip install -e .

# Vérifiez PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Problème GPU/CUDA
```bash
# Vérifiez CUDA
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# Test CPU uniquement
CUDA_VISIBLE_DEVICES="" iol run baseline
```

### Modèle Introuvable
```bash
# Téléchargement manuel
iol download meta-llama/Llama-2-7b-chat-hf

# Ou modèle plus petit pour test
MODEL_ID=gpt2 iol run baseline
```

### Mémoire Insuffisante
```bash
# Utilisez un modèle plus petit
MODEL_ID=gpt2 iol run baseline

# Ou réduisez le batch size
iol run baseline --batch-size 1 --max-new-tokens 32
```

## 📈 Monitoring et Profiling

### Monitoring GPU
```bash
# En parallèle pendant l'exécution
watch -n 1 nvidia-smi

# Logs avec métriques détaillées
iol run baseline --save-json metrics.jsonl
```

### Profiling Avancé
```bash
# Avec profiling Python
python -m cProfile -o profile.stats scripts/run_baseline.py

# Analyse du profil
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"
```

## 🎯 Workflow de Développement

### 1. Développement Local
```bash
# Tests unitaires
pytest tests/ -v

# Linting
ruff check . && ruff format .

# Type checking
mypy inference_optim_llm/
```

### 2. Tests d'Intégration
```bash
# Validation complète
python scripts/validate_setup.py

# Test pipeline complet
iol bench --skip-trtllm  # Baseline seulement
```

### 3. CI/CD
```bash
# Simulation CI locale
pytest tests/ --cov=inference_optim_llm
ruff check .
mypy inference_optim_llm/
```

## 📚 Ressources Supplémentaires

- **Documentation API** : Voir docstrings dans le code
- **Exemples** : Répertoire `notebooks/`
- **Rapports** : Générés dans `reports/`
- **Logs** : Configuration dans `pyproject.toml`

## 🆘 Support

En cas de problème :

1. Vérifiez cette documentation
2. Exécutez `python scripts/validate_setup.py`
3. Consultez les logs détaillés
4. Créez une issue avec les détails de l'erreur