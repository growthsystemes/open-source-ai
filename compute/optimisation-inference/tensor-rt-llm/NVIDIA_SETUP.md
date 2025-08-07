# 🔐 Configuration NVIDIA Registry pour TensorRT-LLM

Pour utiliser les images officielles TensorRT-LLM, vous devez vous authentifier sur le NVIDIA GPU Cloud (NGC) Registry.

## 🚀 Étapes d'Authentification

### 1. Créer un Compte NGC (Gratuit)

1. **Aller sur** [https://ngc.nvidia.com](https://ngc.nvidia.com)
2. **Cliquer** sur "Sign Up" (ou "Se connecter" si vous avez déjà un compte)
3. **Créer un compte** avec votre email (gratuit)
4. **Confirmer** votre email

### 2. Générer une Clé API

1. **Se connecter** sur [ngc.nvidia.com](https://ngc.nvidia.com)
2. **Cliquer** sur votre profil (coin supérieur droit)
3. **Aller dans** "Setup" → "Generate API Key"
4. **Copier** la clé générée (commence par `nvapi-...`)

### 3. Se Connecter avec Docker

```bash
# Se connecter au registry NVIDIA
docker login nvcr.io

# Quand demandé :
# Username: $oauthtoken
# Password: [VOTRE_CLE_API_NGC]
```

**⚠️ Important :**
- **Username** : Tapez exactement `$oauthtoken` (c'est normal !)
- **Password** : Collez votre clé API NGC (commence par `nvapi-`)

### 4. Vérifier la Connexion

```bash
# Test de pull de l'image TensorRT-LLM
docker pull nvcr.io/nvidia/tensorrt_llm:0.7.1-py3
```

## 🖥️ Instructions par Plateforme

### Windows (PowerShell)

```powershell
# Ouvrir PowerShell en tant qu'administrateur
docker login nvcr.io

# Entrer :
# Username: $oauthtoken  
# Password: [votre_clé_API]

# Vérifier
docker pull nvcr.io/nvidia/tensorrt_llm:0.7.1-py3

# Lancer le benchmark
.\run_benchmark.ps1 -Mode all
```

### Linux/macOS

```bash
# Connexion
docker login nvcr.io

# Vérification  
docker pull nvcr.io/nvidia/tensorrt_llm:0.7.1-py3

# Lancer le benchmark
make all
```

## 🔧 Dépannage

### Erreur "403 Forbidden"
```
failed to authorize: failed to fetch oauth token: unexpected status from GET request to https://nvcr.io/proxy_auth?scope=repository%3Anvidia%2Ftensorrt_llm%3Apull: 403 Forbidden
```

**Solutions :**
1. **Vérifier la clé API** : Elle doit commencer par `nvapi-`
2. **Régénérer la clé** sur NGC si elle est expirée
3. **Username correct** : Utilisez exactement `$oauthtoken`

### Erreur "unauthorized"
```
Error response from daemon: pull access denied for nvcr.io/nvidia/tensorrt_llm
```

**Solutions :**
1. **Se déconnecter et reconnecter** :
   ```bash
   docker logout nvcr.io
   docker login nvcr.io
   ```
2. **Vérifier les credentials** avec `docker system info`

### Première utilisation lente
L'image TensorRT-LLM fait ~10GB, le premier téléchargement peut prendre du temps selon votre connexion.

## 🎯 Validation Rapide

Une fois connecté, testez que tout fonctionne :

```bash
# Test complet de l'environnement
python scripts/validate_setup.py

# Test spécifique Docker + NGC
docker run --rm --gpus all nvcr.io/nvidia/tensorrt_llm:0.7.1-py3 nvidia-smi
```

## 🚀 Lancement Post-Authentification

Une fois authentifié, vous pouvez lancer le benchmark :

```bash
# Automatique complet
docker-compose --profile auto up benchmark-full

# Ou par étapes
docker-compose --profile build-only up build-engine
docker-compose --profile pytorch-only up benchmark-pytorch  
docker-compose --profile tensorrt-only up benchmark-tensorrt
docker-compose --profile compare-only up compare-results
```

## 💡 Conseils

1. **Sauvegarder la clé API** dans un gestionnaire de mots de passe
2. **Une seule authentification** par machine (persistent)
3. **Partage d'équipe** : Chaque membre doit avoir son compte NGC
4. **Images locales** : Une fois téléchargée, l'image reste en cache

## 🔄 Alternative Sans Authentification

Si vous préférez éviter l'authentification, je peux adapter le projet pour utiliser des optimisations PyTorch natives qui donnent des résultats comparables. Dites-moi si vous voulez cette approche !

---

**📞 Support :** En cas de problème, consultez la [documentation officielle NGC](https://docs.nvidia.com/ngc/ngc-catalog-user-guide/index.html#registering-activating-ngc-account)
