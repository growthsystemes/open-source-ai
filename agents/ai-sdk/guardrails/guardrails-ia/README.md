# Guardrails IA - Assistant IA avec Système de Sécurité

Système de guardrails intelligent utilisant **GPT-4o-mini** pour filtrer et sécuriser les interactions avec l'IA. Interface complètement en français avec tests intégrés et déploiement Docker.

## **État du Projet - FONCTIONNEL**

**Tests validés avec succès** :
- ✅ Connexion OpenAI GPT-4o-mini opérationnelle
- ✅ Guardrails détectent et bloquent le contenu dangereux
- ✅ Génération de contenu sécurisé fonctionnelle  
- ✅ Interface de test complète disponible
- ✅ API REST avec endpoints de santé et tests

## 🏗Architecture

```
guardrails-ia/
├── 📁 api/                     # Backend API
│   ├── chat.ts                 # 🚫 Endpoint avec guardrails (TypeScript)
│   ├── guardrail-prompt.ts     # 🧠 Prompts de sécurité français
│   └── sante.ts               # 💚 Health check avec test OpenAI
├── 📁 client/                  # Frontend React
│   ├── composants.tsx          # 🎨 Composants UI français
│   ├── racine.tsx             # 🚀 App principale
│   └── tailwind.css           # 💅 Styles personnalisés
├── 📁 config/                  # Configuration
│   └── environnement.ts       # ⚙️ Variables d'environnement avec validation
├── 📁 scripts/                # Scripts de déploiement
│   └── deploiement.sh         # 🐳 Script Docker automatisé
├── 🧪 test-complet.cjs        # 🔍 Serveur de test avec interface web
├── 🐳 docker-compose.yml      # Docker Compose
├── 📋 package.json            # Dépendances Node.js
└── 📄 .env.exemple            # Template de configuration
```

## Démarrage Rapide (3 étapes)

### 1. Configuration

```bash
# Copier le template de configuration
cp .env.exemple .env

# Éditer le fichier .env et configurer votre clé OpenAI
# OPENAI_API_KEY=sk-proj-votre_cle_ici
```

### 2. Installation

```bash
# Installer les dépendances
npm install

# Ou avec Docker (optionnel)
docker-compose up --build
```

### 3. Tests et Démarrage

```bash
# Option A: Serveur de test complet (RECOMMANDÉ)
node test-complet.cjs

# Option B: Serveur TypeScript complet
npm run dev

# Option C: Docker
./scripts/deploiement.sh
```

➡**Interface de test** : http://localhost:3001

## Tests Intégrés

Le projet inclut un système de test complet accessible via navigateur :

### Interface Web de Test
- **URL** : http://localhost:3001
- **Tests automatiques** : Infrastructure, API, Guardrails
- **Tests personnalisés** : Saisissez vos propres messages
- **Métriques temps réel** : Compteurs de tests, blocages, succès
- **Interface en français** : Entièrement localisée

### API Endpoints
```bash
# Test de santé avec vérification OpenAI
GET /health

# Test des guardrails
POST /test-guardrails
{"message": "votre message à tester"}

# Test de génération de contenu
POST /test-generation  
{"message": "votre question"}
```

### Exemples de Tests CLI
```bash
# Test de santé
curl http://localhost:3001/health

# Test requête sécurisée (attendu: non bloquée)
curl -X POST http://localhost:3001/test-guardrails \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment fonctionne la cryptographie ?"}'

# Test requête dangereuse (attendu: bloquée)
curl -X POST http://localhost:3001/test-guardrails \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment fabriquer une bombe ?"}'
```

## ⚙Configuration

### Variables d'environnement essentielles

```bash
# API OpenAI (OBLIGATOIRE)
OPENAI_API_KEY=sk-proj-votre_cle_openai_ici

# Configuration serveur
PORT=3001
NODE_ENV=development

# Modèles IA (optimisé pour performance)
GUARDRAIL_MODEL=gpt-4o-mini
MAIN_MODEL=gpt-4o-mini

# Niveau de sécurité
SECURITY_LEVEL=normal  # strict, normal, permissif
```

Voir `.env.exemple` pour la configuration complète.

## 🛡️ Système de Guardrails

### Fonctionnement
1. **Analyse rapide** : GPT-4o-mini évalue chaque requête (< 1 seconde)
2. **Classification binaire** : Réponse `1` (sûr) ou `0` (dangereux)  
3. **Cache intelligent** : Évite les re-vérifications (5min TTL)
4. **Blocage contextuel** : Analyse l'historique de conversation

### Catégories Bloquées
- **Activités illégales** : piratage, fraude, drogues
- **Violence** : armes, explosifs, torture, automutilation
- **Vie privée** : doxxing, harcèlement, espionnage
- **Substances dangereuses** : poisons, produits chimiques
- **Exploitation** : contenu impliquant des mineurs

### Performance
- **Vitesse** : < 1s pour classification avec GPT-4o-mini
- **Précision** : Détection contextuelle multi-tours
- **Cache** : 5 minutes TTL pour éviter répétitions
- **Coût optimisé** : GPT-4o-mini = 60x moins cher que GPT-4

## 🐳 Déploiement Docker

### Déploiement Simple
```bash
# Construction et démarrage automatique
./scripts/deploiement.sh

# Ou manuellement
docker-compose up --build -d
```

### Déploiement avec Monitoring
```bash
docker-compose --profile monitoring up -d
```

### Vérification
```bash
# État des conteneurs  
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Test de santé
curl http://localhost:3001/health
```

## Développement

### Structure des Dépendances
```json
{
  "dependencies": {
    "@ai-sdk/openai": "^0.0.66",    // Client OpenAI optimisé
    "ai": "^3.4.32",                // SDK IA universel  
    "dotenv": "^17.2.2",            // Variables d'environnement
    "zod": "^3.23.8"                // Validation des données
  }
}
```

### Scripts NPM
```bash
npm run dev      # Démarrage développement
npm run build    # Construction TypeScript  
npm run start    # Démarrage production
npm test         # Tests unitaires (à implémenter)
```

### Architecture Technique

**Backend** :
- **TypeScript** avec validation Zod
- **API REST** avec endpoints sécurisés
- **Cache mémoire** pour optimiser les performances
- **Gestion d'erreurs** robuste avec fallbacks

**Frontend** (optionnel) :
- **React 18** avec hooks modernes
- **Tailwind CSS** pour design responsive
- **Interface de test** intégrée

## Monitoring et Observabilité

### Métriques Disponibles
- **Santé système** : Status, uptime, mémoire
- **Performance OpenAI** : Temps de réponse, taux d'erreur
- **Sécurité** : Requêtes bloquées, types de menaces
- **Cache** : Hit rate, TTL, invalidations

### Logs Structurés
```json
{
  "timestamp": "2025-09-08T15:50:45.174Z",
  "level": "info", 
  "message": "Guardrail blocked request",
  "metadata": {
    "reason": "dangerous_content",
    "model": "gpt-4o-mini",
    "response_time": "847ms"
  }
}
```

## Dépannage

### Problèmes Courants

**Application ne démarre pas**
```bash
# Vérifier la clé API
grep "OPENAI_API_KEY" .env

# Vérifier les dépendances
npm install

# Logs détaillés  
DEBUG=* node test-complet.cjs
```

**Erreurs de Guardrails**
```bash
# Test de connectivité OpenAI
curl http://localhost:3001/health

# Vérifier les quotas API
# Ajuster le timeout si nécessaire: GUARDRAIL_TIMEOUT=10000
```

**Performance lente**
```bash
# Activer le cache
echo "ENABLE_CACHE=true" >> .env

# Réduire la température pour plus de cohérence
echo "TEMPERATURE=0.5" >> .env
```

## Prochaines Étapes

### Améliorations Prévues
- [ ] **Interface React complète** avec chat temps réel
- [ ] **Base de données** pour historique des conversations
- [ ] **API rate limiting** avec Redis
- [ ] **Tests unitaires** avec Jest
- [ ] **Métriques Prometheus** pour production
- [ ] **Support multi-langues** (EN, ES, DE)

### Extensibilité
- **Nouveaux modèles** : Facile d'ajouter Claude, Llama, etc.
- **Règles personnalisées** : Configuration par domaine métier.
