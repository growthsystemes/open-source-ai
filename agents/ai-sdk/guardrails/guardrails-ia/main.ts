import { runLocalDevServer } from '#shared/run-local-dev-server.ts';

/**
 * Point d'entrée principal de l'application Guardrails IA
 * Cette version améliorée inclut des fonctionnalités de sécurité avancées
 * et une interface utilisateur traduite en français
 */
console.log('🚀 Démarrage du serveur Guardrails IA...');
console.log('📋 Fonctionnalités: Guardrails IA, Interface française, Docker ready');

// Configuration du serveur de développement local
await runLocalDevServer({
  root: import.meta.dirname,
  // Port personnalisé pour l'application Guardrails IA
  port: process.env.PORT ? parseInt(process.env.PORT) : 3001,
});

console.log('✅ Serveur Guardrails IA démarré avec succès');