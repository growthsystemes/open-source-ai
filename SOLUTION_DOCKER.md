# 🐳 SOLUTION DOCKER - Fini les Problèmes !

## 🚨 VOUS AVEZ DES ERREURS ? DOCKER = SOLUTION UNIVERSELLE

### ❌ Problèmes Résolus par Docker :
- ❌ `OSError: [WinError 126] torch\lib\shm.dll`
- ❌ `No module named 'tensorrt_llm'`  
- ❌ Conflits de versions Python/PyTorch
- ❌ Problèmes de PATH Windows
- ❌ Visual C++ Redistributables manquants

### ✅ **AVEC DOCKER : TOUT FONCTIONNE**

---

## 🚀 DÉMARRAGE IMMÉDIAT (5 minutes)

### Windows PowerShell
```powershell
# 1. Configuration
cp env.docker.example .env

# 2. Test baseline (CPU)
docker-compose --profile baseline up --build

# 3. Voir les résultats
type reports\baseline.jsonl | Select-Object -First 5
```

### Linux/Mac
```bash
# 1. Configuration
cp env.docker.example .env
chmod +x docker-run.sh

# 2. Test baseline
./docker-run.sh baseline run

# 3. Voir les résultats
head -5 reports/baseline.jsonl
```

---

## 📊 RÉSULTATS ATTENDUS

Après `docker-compose --profile baseline up --build` :

```
✅ Container started
📥 Téléchargement modèle gpt2...
🚀 Lancement baseline avec 10 prompts
✅ Traitement terminé
📁 Résultats sauvés: reports/baseline.jsonl
```

**🎉 Aucune erreur Python, PyTorch ou dépendances !**

---

## 🎯 COMMANDES UTILES

### Test Rapide
```bash
# Baseline CPU seulement
MODEL_ID=gpt2 MAX_NEW_TOKENS=16 docker-compose --profile baseline up

# Avec GPU (si disponible)
CUDA_VISIBLE_DEVICES=0 docker-compose --profile baseline up
```

### Benchmark Complet
```bash
# Baseline + TensorRT-LLM + Analyse
docker-compose --profile bench up --build
```

### Mode Développement
```bash
# Shell interactif dans le conteneur
docker-compose --profile dev run --rm dev bash

# Dans le conteneur :
python -m inference_optim_llm.cli --help
python -m inference_optim_llm.cli run baseline --max-new-tokens 10
```

---

## 🛠️ CONFIGURATION AVANCÉE

### Fichier `.env` (Modifiable)
```bash
MODEL_ID=gpt2              # Modèle à utiliser
BATCH_SIZE=1               # Taille de batch  
MAX_NEW_TOKENS=32          # Tokens à générer
CUDA_VISIBLE_DEVICES=0     # GPU (vide = CPU seulement)
TRT_PRECISION=fp16         # Précision TensorRT
```

### Modèles Testés
```bash
# Rapide (CPU OK)
MODEL_ID=gpt2

# Production légère  
MODEL_ID=microsoft/DialoGPT-small

# Production complète (GPU recommandé)
MODEL_ID=meta-llama/Llama-2-7b-chat-hf
```

---

## 🔧 DÉPANNAGE DOCKER

### Docker non installé ?
- **Windows** : Téléchargez Docker Desktop
- **Linux** : `sudo apt install docker.io docker-compose`
- **Mac** : Téléchargez Docker Desktop

### Erreur de build ?
```bash
# Nettoyage complet
docker-compose down --volumes
docker system prune -a

# Rebuild depuis zéro
docker-compose --profile baseline build --no-cache
```

### Problème GPU ?
```bash
# Test GPU Docker
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Si échec, forcez CPU
CUDA_VISIBLE_DEVICES="" docker-compose --profile baseline up
```

---

## 📈 EXEMPLES CONCRETS

### 1. Test Initial
```bash
# Test le plus simple possible
docker-compose --profile baseline up --build
```

### 2. Benchmark Production
```bash
# Avec modèle Llama et GPU
MODEL_ID=meta-llama/Llama-2-7b-chat-hf \
CUDA_VISIBLE_DEVICES=0 \
docker-compose --profile bench up --build
```

### 3. Développement Interactif
```bash
# Modifier le code et tester
docker-compose --profile dev run --rm dev bash
# Dans le conteneur : éditez et testez
```

---

## 🎉 AVANTAGES DOCKER

| Problème | Solution Docker |
|----------|-----------------|
| Erreurs DLL Windows | ✅ Environnement Linux isolé |
| Conflicts PyTorch | ✅ Versions contrôlées |
| PATH/Scripts | ✅ Configuration automatique |
| TensorRT-LLM manquant | ✅ Installation automatique |
| Modèles téléchargement | ✅ Cache persistant |
| Reproductibilité | ✅ Identique sur tous OS |

**🚀 DOCKER = SOLUTION QUI MARCHE À 100% PARTOUT !**

---

## 📝 AIDE MÉMOIRE

```bash
# Commandes essentielles
docker-compose --profile baseline up    # Test baseline
docker-compose --profile bench up       # Benchmark complet  
docker-compose --profile dev run --rm dev bash  # Shell interactif
docker-compose down --volumes           # Nettoyage

# Voir les résultats
cat reports/baseline.jsonl
cat reports/benchmark_results.md
```

**💡 En cas de doute : UTILISEZ DOCKER !**