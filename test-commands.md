# 🧪 COMMANDES DE TEST - INFERENCE OPTIM LLM

## ✅ **TESTS ÉTAPE PAR ÉTAPE**

### **1. Test Simple - Baseline GPU (Recommandé)**
```powershell
# Test le plus fiable - votre GPU RTX 4070
docker-compose --profile baseline up --build
```
**Attendu :** Latence ~0.6s, TPS ~110 tokens/s, memory_mb et power_w remplis

---

### **2. Test Benchmark Complet**
```powershell
# Baseline + TensorRT-LLM + Analyse
docker-compose --profile bench up --build
```
**Attendu :** Rapport comparatif dans `reports/benchmark_results.md`

---

### **3. Test TensorRT-LLM Seul**
```powershell
# TensorRT-LLM optimisé uniquement
docker-compose --profile trtllm up --build
```
**Attendu :** Performance potentiellement 2-3x meilleure que baseline

---

### **4. Tests de Validation**

#### **4A. Vérifier les résultats**
```powershell
# Voir les métriques baseline
type reports\baseline.jsonl | Select-Object -First 3

# Voir les métriques TensorRT (si disponible)
type reports\trtllm.jsonl | Select-Object -First 3

# Voir le rapport de benchmark
type reports\benchmark_results.md
```

#### **4B. Analyse des performances**
```powershell
# Générer rapport d'analyse
python scripts\benchmark.py --reports-dir reports --output-md reports\analysis.md

# Voir l'analyse
type reports\analysis.md
```

---

### **5. Tests Alternatifs**

#### **5A. Test CPU vs GPU**
```powershell
# 1. Test GPU (actuel)
docker-compose --profile baseline up --build

# 2. Test CPU pour comparaison
(Get-Content .env) -replace 'CUDA_VISIBLE_DEVICES=0', 'CUDA_VISIBLE_DEVICES=""' | Set-Content .env.cpu
docker-compose --env-file .env.cpu --profile baseline up --build

# 3. Remettre GPU
copy .env.cpu .env
(Get-Content .env) -replace 'CUDA_VISIBLE_DEVICES=""', 'CUDA_VISIBLE_DEVICES=0' | Set-Content .env
```

#### **5B. Test avec modèle plus gros**
```powershell
# Modifier pour modèle plus performant
(Get-Content .env) -replace 'MODEL_ID=gpt2', 'MODEL_ID=microsoft/DialoGPT-medium' | Set-Content .env
docker-compose --profile baseline up --build
```

#### **5C. Mode développement interactif**
```powershell
# Shell dans le conteneur pour tests manuels
docker-compose --profile dev run --rm dev bash

# Dans le conteneur :
# python -m inference_optim_llm.cli --help
# python -m inference_optim_llm.cli run baseline --max-new-tokens 10
# nvidia-smi
```

---

### **6. Nettoyage**
```powershell
# Nettoyer les conteneurs et volumes
docker-compose down --volumes

# Nettoyer les images (optionnel)
docker system prune -f
```

---

## 🎯 **ORDRE DE TEST RECOMMANDÉ**

1. **Commande 1** : `docker-compose --profile baseline up --build`
2. **Vérifier** : Latence ~0.6s et memory_mb rempli
3. **Commande 2** : `docker-compose --profile bench up --build`
4. **Analyser** : `type reports\benchmark_results.md`

## 📊 **RÉSULTATS ATTENDUS**

### **Baseline GPU (RTX 4070)**
```json
{"latency": 0.6, "tokens": 64, "memory_mb": 878.7, "power_w": 20.5, "tps": 110}
```

### **TensorRT-LLM (si fonctionne)**
```json
{"latency": 0.2, "tokens": 64, "memory_mb": 1200, "power_w": 25, "tps": 300}
```

**🎉 Si le test 1 marche → Votre projet est 100% fonctionnel avec GPU !**