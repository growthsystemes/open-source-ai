import { openai } from '@ai-sdk/openai';
import {
  convertToModelMessages,
  createUIMessageStream,
  createUIMessageStreamResponse,
  generateText,
  streamText,
  type ModelMessage,
  type UIMessage,
  type UIMessageStreamWriter,
} from 'ai';
import { SYSTEME_GUARDRAIL } from './guardrail-prompt.ts';
import { CONFIG } from '../config/environnement.ts';

/**
 * Interface pour les métriques de sécurité
 */
interface MetriqueSecurite {
  timestamp: number;
  estSure: boolean;
  raisonBlocage?: string;
  tempsVerification: number;
}

/**
 * Cache simple pour éviter les vérifications répétitives
 */
const cacheVerifications = new Map<string, MetriqueSecurite>();

/**
 * Vérifie si une requête est sécurisée en utilisant notre système de guardrails
 * @param messagesModele - Messages de la conversation à analyser
 * @returns Promise<boolean> - true si la requête est sûre, false sinon
 */
const verifierSecuriteRequete = async (
  messagesModele: ModelMessage[],
): Promise<{ estSure: boolean; tempsVerification: number; raisonBlocage?: string }> => {
  const debut = Date.now();
  
  // Générer une clé de cache basée sur le contenu des messages
  const cleCache = messagesModele
    .map(msg => `${msg.role}:${msg.content}`)
    .join('|');
  
  // Vérifier le cache (expire après 5 minutes)
  const cacheExistant = cacheVerifications.get(cleCache);
  if (cacheExistant && Date.now() - cacheExistant.timestamp < 5 * 60 * 1000) {
    return {
      estSure: cacheExistant.estSure,
      tempsVerification: Date.now() - debut,
      raisonBlocage: cacheExistant.raisonBlocage
    };
  }

  try {
    // Analyse de sécurité avec le modèle léger
    const resultatGuardrail = await generateText({
      model: openai(CONFIG.GUARDRAIL_MODEL),
      system: SYSTEME_GUARDRAIL,
      messages: messagesModele,
      maxTokens: 1, // Optimisation : un seul token de réponse (0 ou 1)
      temperature: 0, // Température zéro pour réponse déterministe
    });

    const texte = resultatGuardrail.text.trim();
    const estSure = texte === '1';
    const tempsVerification = Date.now() - debut;
    
    // Mise en cache du résultat
    const metrique: MetriqueSecurite = {
      timestamp: Date.now(),
      estSure,
      raisonBlocage: estSure ? undefined : 'Contenu détecté comme potentiellement dangereux',
      tempsVerification
    };
    cacheVerifications.set(cleCache, metrique);

    return {
      estSure,
      tempsVerification,
      raisonBlocage: metrique.raisonBlocage
    };
    
  } catch (erreur) {
    // En cas d'erreur, on privilégie la sécurité en bloquant
    console.error('Erreur lors de la vérification de sécurité:', erreur);
    return {
      estSure: false,
      tempsVerification: Date.now() - debut,
      raisonBlocage: 'Erreur technique lors de la vérification de sécurité'
    };
  }
};

/**
 * Envoie un message texte vers le client via le stream
 * @param writer - Writer du stream UI
 * @param message - Message à envoyer
 */
const diffuserTexteVersWriter = (
  writer: UIMessageStreamWriter,
  message: string,
) => {
  const id = crypto.randomUUID();
  
  writer.write({
    type: 'text-start',
    id,
  });

  writer.write({
    type: 'text-delta',
    id,
    delta: message,
  });

  writer.write({
    type: 'text-end',
    id,
  });
};

/**
 * Continue le streaming avec le modèle principal après validation sécuritaire
 * @param writer - Writer du stream UI
 * @param messagesModele - Messages validés à traiter
 */
const continuerStreaming = (
  writer: UIMessageStreamWriter,
  messagesModele: ModelMessage[],
) => {
  const resultatStreamTexte = streamText({
    model: openai(CONFIG.MAIN_MODEL),
    messages: messagesModele,
    // Paramètres optimisés pour une meilleure qualité de réponse
    temperature: 0.7,
    maxTokens: 2000,
  });

  writer.merge(resultatStreamTexte.toUIMessageStream());
};

/**
 * Point d'entrée principal de l'API chat
 * Gère le pipeline complet : sécurité → traitement → réponse
 */
export const POST = async (
  req: Request,
): Promise<Response> => {
  try {
    // Conversion des messages UI vers le format du modèle
    const messagesModele = convertToModelMessages(
      (await req.json()).messages,
    );

    // Création du stream de réponse
    const stream = createUIMessageStream({
      execute: async ({ writer }) => {
        // Étape 1: Vérification de sécurité avec métriques
        console.log('🔍 Analyse de sécurité en cours...');
        const {
          estSure,
          tempsVerification,
          raisonBlocage
        } = await verifierSecuriteRequete(messagesModele);

        console.log(`⏱️  Vérification terminée en ${tempsVerification}ms - Résultat: ${estSure ? '✅ Sûr' : '❌ Bloqué'}`);

        // Étape 2: Gestion des requêtes non-sûres
        if (!estSure) {
          const messageBlocage = `🚫 **Demande bloquée par les guardrails de sécurité**

${raisonBlocage}

Je ne peux pas traiter cette demande car elle pourrait violer nos directives de sécurité. 

💡 **Suggestions alternatives :**
- Reformulez votre question de manière plus spécifique
- Consultez notre documentation sur les usages acceptables`;

          diffuserTexteVersWriter(writer, messageBlocage);
          return;
        }

        // Étape 3: Traitement normal de la requête validée
        console.log('✅ Requête validée - Génération de la réponse...');
        continuerStreaming(writer, messagesModele);
      },
    });

    return createUIMessageStreamResponse({
      stream,
      headers: {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
      }
    });
    
  } catch (erreur) {
    console.error('Erreur dans l\'API chat:', erreur);
    
    // Réponse d'erreur sécurisée
    return new Response(
      JSON.stringify({
        error: 'Une erreur technique est survenue. Veuillez réessayer.'
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'X-Content-Type-Options': 'nosniff'
        }
      }
    );
  }
};