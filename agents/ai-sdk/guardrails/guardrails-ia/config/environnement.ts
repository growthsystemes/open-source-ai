/**
 * Configuration centralisée de l'environnement pour Guardrails IA
 * Gestion sécurisée des variables d'environnement avec validation
 */

import { z } from 'zod';

/**
 * Schéma de validation pour les variables d'environnement
 */
const SchemaEnvironnement = z.object({
  // Configuration serveur
  PORT: z.string().transform(Number).default('3001'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('production'),
  
  // Configuration IA
  OPENAI_API_KEY: z.string().min(1, 'Clé API OpenAI requise'),
  GUARDRAIL_MODEL: z.string().default('gpt-4o-mini'),
  MAIN_MODEL: z.string().default('gpt-4o-mini'),
  
  // Configuration guardrails
  SECURITY_LEVEL: z.enum(['strict', 'normal', 'permissif']).default('normal'),
  GUARDRAIL_TIMEOUT: z.string().transform(Number).default('5000'),
  ENABLE_CACHE: z.string().transform(val => val === 'true').default('true'),
  CACHE_TTL: z.string().transform(Number).default('5'),
  
  // Configuration logging
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
  LOG_FORMAT: z.enum(['json', 'text']).default('json'),
  
  // Configuration sécurité
  SESSION_SECRET: z.string().min(32, 'Secret de session trop court (min 32 caractères)'),
  ALLOWED_ORIGINS: z.string().default('http://localhost:3001'),
  
  // Configuration avancée
  AI_TIMEOUT: z.string().transform(Number).default('30000'),
  MAX_TOKENS: z.string().transform(Number).default('2000'),
  TEMPERATURE: z.string().transform(Number).default('0.7'),
  
  // Métriques
  ENABLE_METRICS: z.string().transform(val => val === 'true').default('false'),
  METRICS_INTERVAL: z.string().transform(Number).default('30'),
  
  // Debug
  DEBUG: z.string().transform(val => val === 'true').default('false'),
  ENABLE_HOT_RELOAD: z.string().transform(val => val === 'true').default('false'),
});

/**
 * Type inféré du schéma de configuration
 */
export type ConfigurationEnvironnement = z.infer<typeof SchemaEnvironnement>;

/**
 * Fonction pour charger et valider la configuration
 */
function chargerConfiguration(): ConfigurationEnvironnement {
  try {
    // Validation des variables d'environnement
    const config = SchemaEnvironnement.parse(process.env);
    
    // Validation supplémentaire pour la température
    if (config.TEMPERATURE < 0 || config.TEMPERATURE > 1) {
      throw new Error('TEMPERATURE doit être entre 0.0 et 1.0');
    }
    
    return config;
  } catch (erreur) {
    if (erreur instanceof z.ZodError) {
      console.error('❌ Erreur de configuration d\'environnement:');
      erreur.errors.forEach(err => {
        console.error(`  - ${err.path.join('.')}: ${err.message}`);
      });
    } else {
      console.error('❌ Erreur de configuration:', erreur);
    }
    process.exit(1);
  }
}

/**
 * Configuration globale de l'application
 */
export const CONFIG = chargerConfiguration();

/**
 * Utilitaires pour la configuration
 */
export const UtilitairesConfig = {
  /**
   * Vérifie si l'application est en mode développement
   */
  estDeveloppement: () => CONFIG.NODE_ENV === 'development',
  
  /**
   * Vérifie si l'application est en mode production
   */
  estProduction: () => CONFIG.NODE_ENV === 'production',
  
  /**
   * Récupère la liste des origines autorisées pour CORS
   */
  getOriginesAutorisees: () => CONFIG.ALLOWED_ORIGINS.split(',').map(s => s.trim()),
  
  /**
   * Génère la configuration pour les modèles IA
   */
  getConfigIA: () => ({
    guardrailModel: CONFIG.GUARDRAIL_MODEL,
    mainModel: CONFIG.MAIN_MODEL,
    timeout: CONFIG.AI_TIMEOUT,
    maxTokens: CONFIG.MAX_TOKENS,
    temperature: CONFIG.TEMPERATURE,
  }),
  
  /**
   * Génère la configuration pour les guardrails
   */
  getConfigGuardrails: () => ({
    niveauSecurite: CONFIG.SECURITY_LEVEL,
    timeout: CONFIG.GUARDRAIL_TIMEOUT,
    cacheActive: CONFIG.ENABLE_CACHE,
    dureeCacheTTL: CONFIG.CACHE_TTL,
  }),
  
  /**
   * Génère la configuration de logging
   */
  getConfigLogs: () => ({
    niveau: CONFIG.LOG_LEVEL,
    format: CONFIG.LOG_FORMAT,
    debug: CONFIG.DEBUG,
  }),
  
  /**
   * Affiche un résumé de la configuration au démarrage
   */
  afficherResume: () => {
    console.log('🔧 Configuration Guardrails IA:');
    console.log(`   • Environnement: ${CONFIG.NODE_ENV}`);
    console.log(`   • Port: ${CONFIG.PORT}`);
    console.log(`   • Sécurité: ${CONFIG.SECURITY_LEVEL}`);
    console.log(`   • Cache: ${CONFIG.ENABLE_CACHE ? 'Activé' : 'Désactivé'}`);
    console.log(`   • Métriques: ${CONFIG.ENABLE_METRICS ? 'Activées' : 'Désactivées'}`);
    console.log(`   • Debug: ${CONFIG.DEBUG ? 'Activé' : 'Désactivé'}`);
  }
};

/**
 * Validation de la configuration au chargement du module
 */
if (CONFIG.NODE_ENV === 'production') {
  // Vérifications supplémentaires pour la production
  if (!CONFIG.OPENAI_API_KEY || CONFIG.OPENAI_API_KEY.includes('votre_cle')) {
    console.error('❌ Clé API OpenAI manquante ou invalide en production');
    process.exit(1);
  }
  
  if (!CONFIG.SESSION_SECRET || CONFIG.SESSION_SECRET.includes('votre_secret')) {
    console.error('❌ Secret de session manquant ou par défaut en production');
    process.exit(1);
  }
}

// Export par défaut pour faciliter l'importation
export default CONFIG;