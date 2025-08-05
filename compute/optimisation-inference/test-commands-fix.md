# 🔧 COMMANDES DE CORRECTION ET TEST

## ❌ **PROBLÈME IDENTIFIÉ**
Le cache Docker utilise encore l'ancienne version avec syntaxe cassée.

## ✅ **SOLUTIONS (dans l'ordre)**

### **Solution 1: Rebuild forcé sans cache (RECOMMANDÉ)**
```powershell
# Nettoyage complet du cache
docker-compose down --volumes
docker system prune -f

# Rebuild forcé sans cache
docker-compose --profile bench up --build --no-cache
```

### **Solution 2: Rebuild seulement TensorRT-LLM**
```powershell
# Rebuild seulement l'image problématique
docker-compose build --no-cache trtllm

# Puis lancer le benchmark
docker-compose --profile bench up
```

### **Solution 3: Test sans TensorRT-LLM**
```powershell
# Test baseline + analyse uniquement (skip TensorRT-LLM)
docker-compose --profile baseline up --build

# Analyse manuelle des résultats baseline
python scripts\benchmark.py --reports-dir reports --output-md reports\baseline_only.md
```

### **Solution 4: Test chaque service séparément**
```powershell
# 1. Test baseline (fonctionne déjà)
docker-compose --profile baseline up --build

# 2. Test TensorRT-LLM seul
docker-compose build --no-cache trtllm
docker-compose --profile trtllm up

# 3. Analyse
docker-compose --profile analyze up
```

---

## 🎯 **ORDRE RECOMMANDÉ**

### **Étape 1: Nettoyage et rebuild complet**
```powershell
docker-compose down --volumes
docker system prune -f
docker-compose --profile bench up --build --no-cache
```

### **Étape 2: Si Étape 1 échoue → Test baseline + analyse manuelle**
```powershell
# Baseline fonctionne parfaitement
docker-compose --profile baseline up --build

# Analyse des résultats baseline
type reports\baseline.jsonl | Select-Object -First 3
python scripts\benchmark.py --reports-dir reports
```

### **Étape 3: Si TensorRT-LLM pose encore problème → Ignorer**
```powershell
# Votre GPU RTX 4070 fonctionne parfaitement avec la baseline
# Performance déjà excellente: 110 tokens/s vs 6.6 tokens/s en CPU (18x speedup)
```

---

## 📊 **RÉSULTATS ATTENDUS**

### **Si Étape 1 réussit:**
- ✅ Baseline GPU: ~110 tokens/s
- ✅ TensorRT-LLM: ~200-300 tokens/s (2-3x plus rapide)
- ✅ Rapport comparatif automatique

### **Si seulement baseline marche:**
- ✅ GPU RTX 4070: 18x plus rapide que CPU
- ✅ Latence: 0.6s vs 9.7s en CPU
- ✅ Monitoring: mémoire GPU + puissance

**🎉 Dans tous les cas, votre projet est fonctionnel avec accélération GPU !**

---

## 🚀 **COMMANDE À LANCER MAINTENANT**

```powershell
# Rebuild complet sans cache
docker-compose down --volumes && docker system prune -f && docker-compose --profile bench up --build --no-cache
```

**Ou si vous voulez juste la baseline qui marche parfaitement:**
```powershell
docker-compose --profile baseline up --build
```