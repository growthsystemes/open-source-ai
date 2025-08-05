# 🚀 COMMENCEZ ICI

## ❗ PROBLÈME AVEC `python quick_start.py` ?

### 🪟 **WINDOWS USERS - SUIVEZ CETTE PROCÉDURE :**

```powershell
# 1. Correction automatique des problèmes Windows
python fix_windows_setup.py

# 2. Test rapide pour vérifier
python quick_test_windows.py

# 3. Si tout est OK, validation complète
python scripts/validate_setup.py
```

### 🐧 **LINUX/MAC USERS :**

```bash
# Installation standard
python quick_start.py

# Ou installation manuelle
python setup_dev.py
```

## ✅ APRÈS CORRECTION

Ces commandes doivent marcher :

```powershell
# Test PyTorch
python -c "import torch; print('PyTorch OK')"

# Test package
python -c "from inference_optim_llm.core.metrics import MetricsCollector; print('Package OK')"

# Test CLI
python -m inference_optim_llm.cli --help

# Test baseline rapide
python -m inference_optim_llm.cli run baseline --max-new-tokens 10
```

## 📚 DOCUMENTATION COMPLÈTE

- **Windows** → [README_WINDOWS.md](README_WINDOWS.md)
- **Setup général** → [SETUP.md](SETUP.md)
- **Urgence PyTorch** → [CORRECTION_URGENTE.md](CORRECTION_URGENTE.md)

## 🎯 SÉQUENCE RAPIDE (5 min)

1. `python fix_windows_setup.py` (Windows seulement)
2. `python quick_test_windows.py`
3. `python -m inference_optim_llm.cli run baseline --max-new-tokens 10`

**🎉 Si ça marche → Vous êtes prêt !**