# Dockerfile pour Guardrails IA - Assistant IA avec Système de Sécurité
# Image de base légère avec Node.js
FROM node:20-alpine

# Metadata de l'image
LABEL maintainer="Guardrails-IA"
LABEL description="Assistant IA sécurisé avec système de guardrails français"
LABEL version="1.0"

# Installation des dépendances système nécessaires
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/*

# Création d'un utilisateur non-privilégié pour la sécurité
RUN addgroup -g 1001 -S nodejs && \
    adduser -S explainer -u 1001 -G nodejs

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de configuration de dépendances
# (Ces fichiers sont copiés en premier pour optimiser le cache Docker)
COPY package*.json ./
COPY tsconfig.json ./

# Installation des dépendances incluant TypeScript pour le runtime
ENV NODE_ENV=production
RUN npm install && \
    npm cache clean --force

# Copie du code source de l'application
COPY --chown=explainer:nodejs . .

# Configuration des variables d'environnement
ENV PORT=3001
ENV NODE_ENV=production
ENV TZ=Europe/Paris

# Exposition du port de l'application
EXPOSE $PORT

# Changement vers l'utilisateur non-privilégié
USER explainer

# Vérification de santé pour Docker
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "http.get('http://localhost:3001/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Point d'entrée avec dumb-init pour une gestion correcte des signaux
ENTRYPOINT ["dumb-init", "--"]

# Commande par défaut pour démarrer l'application
CMD ["node", "--experimental-modules", "--loader", "ts-node/esm", "main.ts"]