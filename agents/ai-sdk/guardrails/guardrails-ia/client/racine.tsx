import { useChat } from '@ai-sdk/react';
import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Conteneur, Message, EntreeChat, ChargementMessage } from './composants.tsx';
import './tailwind.css';

/**
 * Configuration des exemples de démonstration
 */
const EXEMPLES_DEMO = [
  {
    titre: "Question sécurisée",
    question: "Comment fonctionne le chiffrement AES en cryptographie ?",
    description: "Exemple d'une question technique légitime"
  },
  {
    titre: "Question éducative", 
    question: "Quels sont les principes de base de la sécurité informatique ?",
    description: "Question d'apprentissage acceptable"
  },
  {
    titre: "Recherche académique",
    question: "Peux-tu m'expliquer l'histoire de l'intelligence artificielle ?",
    description: "Demande de recherche valide"
  }
];

/**
 * Composant principal de l'application Guardrails IA
 */
const Application = () => {
  // État du chat avec configuration
  const { messages, sendMessage, isLoading, error } = useChat({
    api: '/api/chat',
    onError: (erreur) => {
      console.error('Erreur dans le chat:', erreur);
    }
  });

  // État local pour la gestion de l'interface
  const [input, setInput] = useState('');
  const [modeDemo, setModeDemo] = useState(true);
  const [statistiques, setStatistiques] = useState({
    messagesEnvoyes: 0,
    messagesBloque: 0
  });

  // Effet pour compter les statistiques
  useEffect(() => {
    const messagesUtilisateur = messages.filter(m => m.role === 'user').length;
    const messagesBloques = messages.filter(m => 
      m.parts.some(p => p.type === 'text' && p.text.includes('🚫'))
    ).length;

    setStatistiques({
      messagesEnvoyes: messagesUtilisateur,
      messagesBloque: messagesBloques
    });
  }, [messages]);

  // Gestionnaire de soumission du formulaire
  const gererSoumission = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (input.trim()) {
      // Désactiver le mode démo dès le premier message
      if (modeDemo) {
        setModeDemo(false);
      }
      
      // Envoyer le message
      sendMessage({
        text: input.trim(),
      });
      
      // Réinitialiser le champ de saisie
      setInput('');
    }
  };

  // Gestionnaire pour les exemples de démonstration
  const chargerExemple = (exemple: typeof EXEMPLES_DEMO[0]) => {
    setInput(exemple.question);
    setModeDemo(false);
  };

  return (
    <Conteneur>
      {/* Mode démonstration - affiché au début */}
      {modeDemo && messages.length === 0 && (
        <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg p-6 border border-blue-500/20 mb-6">
          <h2 className="text-xl font-semibold text-blue-300 mb-3">
            🎯 Mode Démonstration
          </h2>
          <p className="text-gray-300 mb-4">
            Essayez ces exemples pour découvrir comment fonctionne le système de guardrails :
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {EXEMPLES_DEMO.map((exemple, index) => (
              <button
                key={index}
                onClick={() => chargerExemple(exemple)}
                className="text-left p-3 bg-gray-800 hover:bg-gray-700 rounded border border-gray-600 hover:border-blue-500 transition-colors group"
              >
                <div className="font-medium text-green-300 text-sm mb-1 group-hover:text-green-200">
                  {exemple.titre}
                </div>
                <div className="text-xs text-gray-400 mb-2">
                  {exemple.description}
                </div>
                <div className="text-xs text-gray-500 italic">
                  "{exemple.question.substring(0, 50)}..."
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Statistiques de session */}
      {messages.length > 0 && (
        <div className="flex justify-center mb-4">
          <div className="bg-gray-800 rounded-lg px-4 py-2 flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-gray-300">Messages: {statistiques.messagesEnvoyes}</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-red-500 rounded-full"></span>
              <span className="text-gray-300">Bloqués: {statistiques.messagesBloque}</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span className="text-gray-300">Taux sécurité: {
                statistiques.messagesEnvoyes > 0 
                  ? Math.round((1 - statistiques.messagesBloque / statistiques.messagesEnvoyes) * 100)
                  : 100
              }%</span>
            </div>
          </div>
        </div>
      )}

      {/* Affichage des messages de conversation */}
      <div className="space-y-4 mb-6">
        {messages.map((message) => (
          <Message
            key={message.id}
            role={message.role}
            parts={message.parts}
          />
        ))}
        
        {/* Indicateur de chargement */}
        {isLoading && <ChargementMessage />}
        
        {/* Affichage des erreurs */}
        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <span className="text-red-400">⚠️</span>
              <span className="text-red-300 font-medium">Erreur technique</span>
            </div>
            <p className="text-red-200 text-sm mt-1">
              Une erreur est survenue lors de la communication avec le serveur. Veuillez réessayer.
            </p>
          </div>
        )}
      </div>

      {/* Message d'accueil si aucune conversation */}
      {messages.length === 0 && !modeDemo && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🤖</div>
          <h2 className="text-2xl font-bold text-gray-300 mb-2">
            Assistant IA Sécurisé
          </h2>
          <p className="text-gray-400 max-w-md mx-auto">
            Posez vos questions en toute confiance. Notre système de guardrails 
            analysera chaque demande pour garantir des échanges sécurisés.
          </p>
        </div>
      )}

      {/* Composant de saisie - toujours en bas */}
      <EntreeChat
        input={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={gererSoumission}
        estEnTraitement={isLoading}
      />
    </Conteneur>
  );
};

// Point d'entrée de l'application
const racine = createRoot(document.getElementById('root')!);
racine.render(<Application />);