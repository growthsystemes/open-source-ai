/**
 * Endpoint de vérification de santé pour Guardrails IA
 * Fournit des informations sur l'état de l'application et des services
 */

import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';
import { CONFIG } from '../config/environnement.ts';

/**
 * Interface pour le rapport de santé
 */
interface RapportSante {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  environment: string;
  services: {
    [key: string]: {
      status: 'up' | 'down' | 'degraded';
      responseTime?: number;
      error?: string;
      lastCheck: string;
    };
  };
  metrics: {
    uptime: number;
    memoryUsage: NodeJS.MemoryUsage;
    processId: number;
  };
}

/**
 * Teste la connectivité avec l'API Google AI
 */
async function testerConnexionIA(): Promise<{ status: 'up' | 'down'; responseTime?: number; error?: string }> {
  const debut = Date.now();
  
  try {
    // Test simple avec le modèle de guardrail
    await generateText({
      model: openai(CONFIG.GUARDRAIL_MODEL),
      prompt: '1', // Prompt minimal pour tester la connectivité
      maxTokens: 1,
    });
    
    return {
      status: 'up',
      responseTime: Date.now() - debut
    };
  } catch (erreur) {
    return {
      status: 'down',
      error: erreur instanceof Error ? erreur.message : 'Erreur inconnue',
      responseTime: Date.now() - debut
    };
  }
}

/**
 * Génère un rapport de santé complet
 */
async function genererRapportSante(): Promise<RapportSante> {
  const timestampActuel = new Date().toISOString();
  
  // Test des services externes
  const [testIA] = await Promise.all([
    testerConnexionIA()
  ]);
  
  // Calcul du statut global
  let statusGlobal: RapportSante['status'] = 'healthy';
  
  if (testIA.status === 'down') {
    statusGlobal = 'unhealthy';
  } else if (testIA.status === 'degraded' || (testIA.responseTime && testIA.responseTime > 5000)) {
    statusGlobal = 'degraded';
  }
  
  // Métriques système
  const uptime = process.uptime();
  const memoryUsage = process.memoryUsage();
  
  return {
    status: statusGlobal,
    timestamp: timestampActuel,
    version: '1.0.0',
    environment: CONFIG.NODE_ENV,
    services: {
      'google-ai': {
        ...testIA,
        lastCheck: timestampActuel
      }
    },
    metrics: {
      uptime,
      memoryUsage,
      processId: process.pid
    }
  };
}

/**
 * Endpoint de vérification de santé simple (pour Docker healthcheck)
 */
export const GET = async (): Promise<Response> => {
  try {
    const rapport = await genererRapportSante();
    
    // Code de statut HTTP basé sur l'état de santé
    const statusCode = rapport.status === 'healthy' ? 200 : 
                      rapport.status === 'degraded' ? 200 : 503;
    
    return new Response(
      JSON.stringify(rapport, null, 2),
      {
        status: statusCode,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
      }
    );
  } catch (erreur) {
    // En cas d'erreur lors de la génération du rapport
    const rapportErreur: Partial<RapportSante> = {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      environment: CONFIG.NODE_ENV
    };
    
    return new Response(
      JSON.stringify({
        ...rapportErreur,
        error: erreur instanceof Error ? erreur.message : 'Erreur interne'
      }, null, 2),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
};

/**
 * Endpoint de santé détaillé pour monitoring avancé
 */
export const POST = async (): Promise<Response> => {
  try {
    const rapport = await genererRapportSante();
    
    // Ajout d'informations détaillées pour le monitoring
    const rapportDetaille = {
      ...rapport,
      details: {
        configuration: {
          securityLevel: CONFIG.SECURITY_LEVEL,
          cacheEnabled: CONFIG.ENABLE_CACHE,
          metricsEnabled: CONFIG.ENABLE_METRICS
        },
        runtime: {
          nodeVersion: process.version,
          platform: process.platform,
          arch: process.arch
        }
      }
    };
    
    return new Response(
      JSON.stringify(rapportDetaille, null, 2),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        }
      }
    );
  } catch (erreur) {
    return new Response(
      JSON.stringify({
        status: 'unhealthy',
        error: erreur instanceof Error ? erreur.message : 'Erreur interne',
        timestamp: new Date().toISOString()
      }),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
};