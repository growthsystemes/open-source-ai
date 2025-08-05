# 🚨 CORRECTION URGENTE - Windows PyTorch

Vous avez cette erreur ? **SUIVEZ CE GUIDE EXACTEMENT** ⬇️

```
OSError: [WinError 126] Le module spécifié est introuvable. 
Error loading "torch\lib\shm.dll"
```

## ⚡ SOLUTION IMMÉDIATE (5 minutes)

### Étape 1 : Script de Correction
```powershell
python fix_windows_setup.py
```

### Étape 2 : Test Rapide
```powershell
python quick_test_windows.py
```

### Étape 3 : Si Encore des Erreurs
```powershell
# Désinstallation complète PyTorch
pip uninstall torch torchvision torchaudio -y

# Réinstallation PyTorch CPU (STABLE)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Test import
python -c "import torch; print('PyTorch OK')"
```

## ✅ VALIDATION

Après correction, ces commandes doivent TOUTES marcher :

```powershell
# 1. Test PyTorch
python -c "import torch; print('PyTorch:', torch.__version__)"

# 2. Test package
python -c "from inference_optim_llm.core.metrics import MetricsCollector; print('Package OK')"

# 3. Test CLI
python -m inference_optim_llm.cli --help
```

## 🔧 SI PROBLÈME PERSISTE

### Option A : Visual C++ Redistributables
1. Téléchargez : https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Installez et redémarrez
3. Relancez `python fix_windows_setup.py`

### Option B : Environnement Conda (Recommandé)
```powershell
# Installez Miniconda si pas fait
# Puis :
conda create -n optim-llm python=3.10
conda activate optim-llm
conda install pytorch cpuonly -c pytorch
pip install -e .
```

## 🎯 TEST FINAL

```powershell
# Test complet (doit marcher à 100%)
python scripts/validate_setup.py
```

**🎉 Si ça marche → Projet fonctionnel !**

---

## 📞 Besoin d'Aide ?

1. **Copiez la sortie complète** de `python fix_windows_setup.py`
2. **Indiquez votre version Python** : `python --version`
3. **Indiquez si vous avez Visual Studio installé**

Le problème est **résolu dans 99% des cas** avec les étapes ci-dessus !