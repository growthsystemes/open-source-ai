# 🚀 Installation GPU + Docker pour Windows

Guide complet pour utiliser votre **RTX 4070** avec Docker.

## 🎯 Objectif
Permettre à Docker d'accéder à votre GPU NVIDIA pour accélérer l'inférence LLM.

---

## 📋 Prérequis

✅ **GPU NVIDIA** : RTX 4070 (déjà ✅)  
✅ **Pilotes NVIDIA** : Version récente (déjà ✅)  
✅ **Docker Desktop** : Installé (déjà ✅)  
🔄 **WSL2** : À configurer  
🔄 **NVIDIA Container Toolkit** : À installer  

---

## 🔧 Installation Étape par Étape

### **Étape 1 : Configuration Docker Desktop**

1. **Ouvrez Docker Desktop**
2. **Settings** → **General**
3. ✅ Activez **"Use the WSL 2 based engine"**
4. **Settings** → **Resources** → **WSL Integration**  
5. ✅ Activez **"Enable integration with my default WSL distro"**
6. **Apply & Restart**

### **Étape 2 : Installation WSL2 (si nécessaire)**

```powershell
# Dans PowerShell Administrateur
wsl --install
# Redémarrez votre PC après installation
```

### **Étape 3 : Installation NVIDIA Container Toolkit**

```powershell
# Méthode automatique
powershell -ExecutionPolicy Bypass -File install-gpu-docker.ps1

# OU Méthode manuelle (voir ci-dessous)
```

### **Étape 4 : Installation Manuelle (Alternative)**

Dans **WSL2** (Ubuntu) :

```bash
# 1. Update système
sudo apt update

# 2. Ajout du repository NVIDIA
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/ /" | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 3. Installation
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 4. Configuration Docker
sudo nvidia-ctk runtime configure --runtime=docker

# 5. Redémarrer Docker (via Docker Desktop)
```

### **Étape 5 : Redémarrage Docker Desktop**

1. **Fermez complètement Docker Desktop** (Exit dans la barre de tâches)
2. **Relancez Docker Desktop**
3. **Attendez le démarrage complet**

---

## 🧪 Tests de Validation

### **Test 1 : Accès GPU de base**
```powershell
docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu20.04 nvidia-smi
```
**Attendu :** Sortie nvidia-smi avec votre RTX 4070

### **Test 2 : Notre projet baseline**
```powershell
docker-compose --profile baseline up --build
```
**Attendu :** Utilisation GPU + métriques `memory_mb` et `power_w` remplies

### **Test 3 : Benchmark complet**
```powershell
docker-compose --profile bench up --build
```
**Attendu :** Baseline GPU + TensorRT-LLM GPU

---

## 🔍 Résolution de Problèmes

### ❌ **"unknown flag: --gpus"**
- **Cause :** Version Docker trop ancienne
- **Solution :** Mettez à jour Docker Desktop

### ❌ **"nvidia runtime not found"**
- **Cause :** NVIDIA Container Toolkit mal installé
- **Solution :** Réinstallez via WSL2 + redémarrez Docker Desktop

### ❌ **"manifest not found" pour images CUDA**
- **Cause :** Problème réseau ou version image
- **Solution :** Essayez `nvidia/cuda:11.8-base-ubuntu20.04`

### ❌ **GPU non détecté dans le conteneur**
- **Cause :** Docker Desktop ne voit pas WSL2
- **Solution :** 
  1. Redémarrez complètement le PC
  2. Vérifiez Settings WSL Integration dans Docker Desktop

---

## 📊 Validation Réussie

Si tout fonctionne, vous devriez voir :

```json
{"prompt": "Hello", "latency": 2.1, "tokens": 64, "memory_mb": 1024.5, "power_w": 120.8, "tps": 30.5}
```

**Notez :**
- ✅ `memory_mb` et `power_w` avec valeurs réelles (pas NaN)
- ✅ `tps` (tokens/sec) plus élevé qu'en CPU
- ✅ `latency` réduite

---

## 🚀 Commandes Finales

```powershell
# Test baseline GPU
docker-compose --profile baseline up --build

# Benchmark complet GPU
docker-compose --profile bench up --build

# Mode développement avec GPU
docker-compose --profile dev run --rm dev bash
```

---

## 💡 Tips Performance

### **Configuration GPU Optimale**
Modifiez `.env` :
```bash
MODEL_ID=gpt2                    # Test rapide
MODEL_ID=microsoft/DialoGPT-small # Production légère
BATCH_SIZE=4                     # Augmentez si GPU le permet
MAX_NEW_TOKENS=128              # Plus de tokens
TRT_PRECISION=fp16              # Précision optimale
```

### **Monitoring GPU**
```powershell
# Pendant l'exécution, dans un autre terminal :
nvidia-smi -l 1  # Rafraîchit chaque seconde
```

**🎉 Avec ces étapes, votre RTX 4070 sera pleinement exploitée !**