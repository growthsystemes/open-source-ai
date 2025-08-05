# 🚀 Commandes Rapides - Inference-Optim-LLM

## 📊 **Tests de Performance Recommandés**

### **🏆 Configuration Optimale (Meilleurs Gains)**
```bash
# Benchmark complet optimisé
docker-compose run --rm baseline run baseline \
  --prompts-file data/prompts_medium.txt \
  --max-new-tokens 200 \
  --batch-size 4 \
  --save-json reports/optimal.jsonl
```
**Résultat attendu :** ~101 TPS, 1.8s latence, 882MB VRAM

---

### **⚡ Tests Comparatifs Rapides**

```bash
# 1. Test baseline rapide (référence)
docker-compose --profile baseline up

# 2. Test benchmark complet
docker-compose --profile bench up

# 3. Test prompts moyens vs courts
docker-compose run --rm baseline run baseline --prompts-file data/prompts_medium.txt --max-new-tokens 200 --save-json reports/medium.jsonl
docker-compose run --rm baseline run baseline --prompts-file data/prompts.txt --max-new-tokens 64 --save-json reports/short.jsonl
```

---

## 📈 **Analyse des Résultats**

```bash
# Voir les premiers résultats
type reports\baseline.jsonl | Select-Object -First 3
type reports\trtllm.jsonl | Select-Object -First 3

# Comparer les fichiers
dir reports\

# Analyser les gains
python scripts/benchmark.py --reports-dir reports --output-md reports/analysis.md
```

---

## 🛠️ **Maintenance & Debug**

```bash
# Rebuild complet
docker-compose build --no-cache

# Logs détaillés
docker-compose --profile bench up --build

# Nettoyer les containers
docker-compose down --volumes --remove-orphans

# Voir l'utilisation GPU en temps réel
nvidia-smi -l 1
```

---

## 🎯 **Configurations par Use Case**

### **Development/Test Rapide**
```bash
docker-compose run --rm baseline run baseline --prompts-file data/prompts.txt --max-new-tokens 64 --quiet
```

### **Production Simulation** 
```bash
docker-compose run --rm baseline run baseline --prompts-file data/prompts_medium.txt --max-new-tokens 200 --batch-size 4 --save-json reports/prod_sim.jsonl
```

### **Stress Test**
```bash
docker-compose run --rm baseline run baseline --prompts-file data/prompts_long.txt --max-new-tokens 500 --batch-size 8 --save-json reports/stress.jsonl
```

---

## 📊 **Métriques Attendues (RTX 4070)**

| **Configuration** | **TPS** | **Latence** | **VRAM** | **Commande** |
|-------------------|---------|-------------|----------|--------------|
| Courts (64T) | ~70 | 0.8s | 1513MB | `--max-new-tokens 64` |
| Moyens (200T) | ~81 | 2.4s | 882MB | `--max-new-tokens 200` |
| Batch x4 (200T) | ~101 | 1.8s | 882MB | `--batch-size 4 --max-new-tokens 200` |

---

## 🚨 **Troubleshooting Rapide**

```bash
# Erreur CUDA/GPU
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Erreur TensorRT-LLM (normal en fallback)
# ⚠️ TensorRT-LLM non disponible - utilisation du fallback baseline GPU

# Rebuild si cache corrompu
docker-compose build --no-cache trtllm

# Test GPU direct
docker run --rm --gpus all pytorch/pytorch:latest python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

## 🎯 **One-Liner pour Demo**

```bash
# Demo complète en une commande
docker-compose --profile bench up && echo "✅ Voir reports/ pour les résultats détaillés"
```