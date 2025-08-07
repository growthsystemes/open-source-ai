# 🚀 Guide de Démarrage Rapide - TensorRT-LLM Benchmark

Benchmarker TensorRT-LLM vs PyTorch en 5 minutes !

## ⚡ Démarrage Ultra-Rapide

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd tensor-rt-llm

# 2. 🔐 OBLIGATOIRE : S'authentifier sur NVIDIA NGC
.\setup_nvidia_auth.ps1     # Windows
./setup_nvidia_auth.sh      # Linux/macOS

# 3. Lancer le benchmark complet (20-30 min)
docker-compose --profile auto up benchmark-full

# 4. Voir les résultats
ls data/results/
```

## 🛠️ Options de Lancement

### Windows (PowerShell)
```powershell
# Benchmark complet
.\run_benchmark.ps1 -Mode all

# Étapes individuelles
.\run_benchmark.ps1 -Mode build      # Construction moteur
.\run_benchmark.ps1 -Mode pytorch    # Benchmark PyTorch
.\run_benchmark.ps1 -Mode tensorrt   # Benchmark TensorRT
.\run_benchmark.ps1 -Mode compare    # Comparaison

# Mode interactif
.\run_benchmark.ps1 -Mode interactive
```

### Linux/macOS (Make)
```bash
# Benchmark complet
make all

# Ou automatique (tout en une fois)
make auto

# Étapes individuelles
make build      # Construction moteur
make pytorch    # Benchmark PyTorch  
make tensorrt   # Benchmark TensorRT
make compare    # Comparaison

# Mode interactif
make interactive

# Aide
make help
```

### Docker Compose Direct
```bash
# Benchmark complet automatique
docker-compose --profile auto up benchmark-full

# Étapes manuelles
docker-compose --profile build-only up build-engine
docker-compose --profile pytorch-only up benchmark-pytorch
docker-compose --profile tensorrt-only up benchmark-tensorrt
docker-compose --profile compare-only up compare-results

# Mode interactif
docker-compose --profile manual run --rm tensorrt-llm-benchmark
```

## 🔍 Validation de l'Environnement

Avant de commencer, validez votre setup :

```bash
# Validation automatique
python scripts/validate_setup.py

# Test GPU Docker
docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
```

## 📊 Résultats

Après exécution, consultez `data/results/` :

- **`pytorch_benchmark.json`** - Métriques PyTorch détaillées
- **`tensorrt_benchmark.json`** - Métriques TensorRT détaillées
- **`benchmark_comparison_report.json`** - Rapport complet
- **`benchmark_comparison.png`** - Graphiques de comparaison

### Exemple de Résultats

```json
{
  "speedup_analysis": {
    "latency_improvement": {
      "pytorch_ms": 1250.5,
      "tensorrt_ms": 345.2,
      "speedup_factor": 3.62,
      "improvement_percent": 72.4
    },
    "throughput_improvement": {
      "pytorch_tokens_per_sec": 18.7,
      "tensorrt_tokens_per_sec": 67.8,
      "speedup_factor": 3.63,
      "improvement_percent": 262.6
    }
  }
}
```

## 🎮 Configuration GPU

### NVIDIA GPUs Testés
- ✅ **RTX 4090** - Excellent (12+ GB VRAM)
- ✅ **RTX 4080** - Très bon (10+ GB VRAM)  
- ✅ **RTX 3080** - Bon (8+ GB VRAM)
- ⚠️ **RTX 3060** - Limité (6 GB VRAM)
- ❌ **GTX 1660** - Incompatible (pas de Tensor Cores)

### Prérequis
- **VRAM**: 6+ GB (8+ GB recommandé)
- **Drivers**: 525+ 
- **CUDA**: 12.0+ (inclus dans l'image Docker)
- **Docker**: Avec support GPU

## 🔧 Dépannage Express

### Erreur "CUDA out of memory"
```bash
# Réduire la taille de batch/séquence
# Modifier scripts/build_engine.sh:
--max_batch_size 1
--max_input_len 256
--max_output_len 256
```

### Erreur "Docker can't access GPU"
```bash
# Windows (Docker Desktop)
# Activer "Use WSL 2 based engine" + "GPU support"

# Linux
sudo apt install nvidia-docker2
sudo systemctl restart docker
```

### Erreur "TensorRT engine not found"
```bash
# Reconstruire le moteur
docker-compose --profile build-only up build-engine
```

## 📈 Résultats Attendus

### TinyLlama 1.1B sur RTX 4090
| Métrique | PyTorch | TensorRT | Gain |
|----------|---------|----------|------|
| Latence | ~1200ms | ~350ms | **3.4x** |
| Débit | ~20 tok/s | ~70 tok/s | **3.5x** |
| Mémoire | ~2.8GB | ~2.0GB | **-29%** |

### TinyLlama 1.1B sur RTX 3080
| Métrique | PyTorch | TensorRT | Gain |
|----------|---------|----------|------|
| Latence | ~1800ms | ~550ms | **3.3x** |
| Débit | ~15 tok/s | ~50 tok/s | **3.3x** |
| Mémoire | ~3.1GB | ~2.2GB | **-29%** |

## 🚀 Prochaines Étapes

1. **Tester d'autres modèles** :
   ```bash
   # Modifier MODEL_NAME dans scripts/build_engine.sh
   MODEL_NAME="microsoft/DialoGPT-medium"
   ```

2. **Optimisations avancées** :
   ```bash
   # Ajouter dans build_engine.sh
   --use_fused_mlp
   --use_gpt_attention_plugin
   --int8  # Quantization
   ```

3. **Batch processing** :
   ```bash
   # Augmenter le batch size
   --max_batch_size 4
   ```

## 📚 Documentation Complète

- Voir [README.md](README.md) pour la documentation complète
- Configuration avancée dans [config.example.env](config.example.env)
- Scripts détaillés dans [scripts/](scripts/)

---

**🎯 TL;DR** : `docker-compose --profile auto up benchmark-full` et attendez 20-30 minutes ! 🚀
