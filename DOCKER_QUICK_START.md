# 🐳 DOCKER QUICK START

## ❗ PROBLÈMES D'ENVIRONNEMENT ? DOCKER EST LA SOLUTION !

### 🚀 **DÉMARRAGE EN 3 ÉTAPES (10 minutes)**

#### 1. Préparation (30 secondes)
```bash
# Copiez la configuration
cp env.docker.example .env

# Linux/Mac seulement
chmod +x docker-run.sh
```

#### 2. Test Baseline CPU (5 minutes)
```bash
# Linux/Mac
./docker-run.sh baseline run

# Windows
docker-compose --profile baseline up --build
```

#### 3. Test Complet GPU (optionnel)
```bash
# Linux/Mac
./docker-run.sh bench run

# Windows
docker-compose --profile bench up --build
```

---

## ✅ **APRÈS EXÉCUTION**

### Résultats dans `./reports/` :
- `baseline.jsonl` - Métriques détaillées
- `benchmark_results.md` - Rapport comparatif

### Commandes de Test :
```bash
# Voir les résultats
cat reports/baseline.jsonl | head -5
cat reports/benchmark_results.md

# Mode développement
./docker-run.sh dev shell  # Linux/Mac
docker-compose --profile dev run --rm dev bash  # Windows
```

---

## 🎯 **EXEMPLES PRATIQUES**

### Test Rapide GPT-2
```bash
MODEL_ID=gpt2 MAX_NEW_TOKENS=16 ./docker-run.sh baseline run
```

### Benchmark Production Llama
```bash
MODEL_ID=meta-llama/Llama-2-7b-chat-hf ./docker-run.sh bench run
```

### Mode CPU seulement
```bash
CUDA_VISIBLE_DEVICES="" ./docker-run.sh baseline run
```

---

## 🛠️ **COMMANDES UTILES**

| Action | Linux/Mac | Windows |
|--------|-----------|---------|
| Baseline | `./docker-run.sh baseline run` | `docker-compose --profile baseline up` |
| TensorRT | `./docker-run.sh trtllm run` | `docker-compose --profile trtllm up` |
| Benchmark | `./docker-run.sh bench run` | `docker-compose --profile bench up` |
| Shell | `./docker-run.sh dev shell` | `docker-compose run --rm dev bash` |
| Nettoyage | `./docker-run.sh clean` | `docker-compose down --volumes` |

---

## 🚨 **RÉSOLUTION PROBLÈMES**

### Docker non installé ?
- **Windows** : Docker Desktop
- **Linux** : `sudo apt install docker.io docker-compose`
- **Mac** : Docker Desktop

### Erreur GPU ?
```bash
# Test GPU
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Si échec, utilisez CPU
CUDA_VISIBLE_DEVICES="" ./docker-run.sh baseline run
```

### Problème Build ?
```bash
# Nettoyage complet
./docker-run.sh clean
docker system prune -a

# Rebuild
./docker-run.sh baseline build
```

---

## 🎉 **AVANTAGES DOCKER**

- ✅ **Zéro configuration environnement**
- ✅ **Fonctionne sur Windows/Linux/Mac**
- ✅ **Pas d'erreur PyTorch/CUDA**
- ✅ **Installation automatique modèles**
- ✅ **Reproductible à 100%**

**🚀 UTILISEZ DOCKER = FINI LES PROBLÈMES !**