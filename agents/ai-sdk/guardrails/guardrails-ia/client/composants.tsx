import type { UIDataTypes, UIMessagePart, UITools } from 'ai';
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

/**
 * Composant conteneur principal avec design amélioré
 */
export const Conteneur = (props: {
  children: React.ReactNode;
}) => {
  return (
    <div className="flex flex-col w-full max-w-4xl py-8 mx-auto px-4">
      {/* En-tête de l'application */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-blue-400 mb-2">
          🛡️ Guardrails IA
        </h1>
        <p className="text-gray-400 text-sm">
          Assistant IA sécurisé avec protection avancée contre les contenus dangereux
        </p>
      </div>
      
      {/* Zone de contenu principal */}
      <div className="flex-1 space-y-4">
        {props.children}
      </div>
      
      {/* Pied de page avec informations */}
      <div className="mt-8 pt-4 border-t border-gray-700 text-center text-xs text-gray-500">
        <p>🔒 Toutes les conversations sont analysées par nos systèmes de sécurité</p>
        <p>⚡ Propulsé par Gemini 2.0 Flash avec guardrails français</p>
      </div>
    </div>
  );
};

/**
 * Composant de message amélioré avec formatage et indicateurs
 */
export const Message = ({
  role,
  parts,
}: {
  role: string;
  parts: UIMessagePart<UIDataTypes, UITools>[];
}) => {
  // Déterminer le style selon le rôle
  const estUtilisateur = role === 'user';
  const prefixe = estUtilisateur ? '👤 Vous' : '🤖 Assistant';
  const couleurFond = estUtilisateur ? 'bg-blue-900/30' : 'bg-gray-800/50';
  const couleurBordure = estUtilisateur ? 'border-blue-500/30' : 'border-gray-600/30';

  // Extraire le texte de toutes les parties du message
  const texte = parts
    .map((partie) => {
      if (partie.type === 'text') {
        return partie.text;
      }
      return '';
    })
    .join('');

  // Détecter si le message est un blocage de sécurité
  const estBlocage = texte.includes('🚫') || texte.includes('bloquée');

  return (
    <div className={`p-4 rounded-lg border ${couleurFond} ${couleurBordure} ${estBlocage ? 'border-red-500/50' : ''}`}>
      <div className="flex items-start space-x-3">
        <div className={`font-semibold text-sm ${estUtilisateur ? 'text-blue-300' : 'text-green-300'}`}>
          {prefixe}
        </div>
        <div className="flex-1">
          <div className={`prose prose-invert max-w-none ${estBlocage ? 'prose-red' : ''}`}>
            <ReactMarkdown
              components={{
                // Personnalisation des liens
                a: ({ href, children }) => (
                  <a 
                    href={href} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline"
                  >
                    {children}
                  </a>
                ),
                // Personnalisation du code
                code: ({ children, className }) => (
                  <code className={`bg-gray-700 px-1 py-0.5 rounded text-sm ${className || ''}`}>
                    {children}
                  </code>
                )
              }}
            >
              {texte}
            </ReactMarkdown>
          </div>
        </div>
        {/* Timestamp */}
        <div className="text-xs text-gray-500">
          {new Date().toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};

/**
 * Composant d'entrée de chat amélioré avec suggestions et validations
 */
export const EntreeChat = ({
  input,
  onChange,
  onSubmit,
  estEnTraitement = false
}: {
  input: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  estEnTraitement?: boolean;
}) => {
  const [suggestions] = useState([
    "Expliquez-moi le principe de la cryptographie",
    "Comment sécuriser un réseau d'entreprise ?",
    "Quels sont les fondements de l'intelligence artificielle ?",
    "Comment fonctionne l'apprentissage automatique ?"
  ]);

  const [suggestionSelectionnee, setSuggestionSelectionnee] = useState<string | null>(null);

  const gererSuggestion = (suggestion: string) => {
    const event = {
      target: { value: suggestion }
    } as React.ChangeEvent<HTMLTextAreaElement>;
    onChange(event);
    setSuggestionSelectionnee(suggestion);
  };

  return (
    <div className="sticky bottom-0 bg-gray-900/95 backdrop-blur-sm p-4 border-t border-gray-700">
      {/* Suggestions rapides */}
      {input.length === 0 && (
        <div className="mb-3">
          <p className="text-xs text-gray-400 mb-2">💡 Suggestions :</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => gererSuggestion(suggestion)}
                className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Formulaire de saisie */}
      <form onSubmit={onSubmit} className="space-y-3">
        <div className="relative">
          <textarea
            className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 resize-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none transition-colors"
            value={input}
            placeholder="Posez votre question en toute sécurité..."
            onChange={onChange}
            rows={3}
            disabled={estEnTraitement}
          />
          
          {/* Compteur de caractères */}
          <div className="absolute bottom-2 right-2 text-xs text-gray-500">
            {input.length}/1000
          </div>
        </div>

        {/* Boutons d'action */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span>Guardrails actifs</span>
          </div>
          
          <div className="flex space-x-2">
            {input.length > 0 && (
              <button
                type="button"
                onClick={() => onChange({ target: { value: '' } } as React.ChangeEvent<HTMLTextAreaElement>)}
                className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors"
                disabled={estEnTraitement}
              >
                Effacer
              </button>
            )}
            
            <button
              type="submit"
              disabled={estEnTraitement || input.trim().length === 0}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded font-medium transition-colors flex items-center space-x-2"
            >
              {estEnTraitement ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Analyse...</span>
                </>
              ) : (
                <>
                  <span>Envoyer</span>
                  <span>🚀</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

/**
 * Composant d'état de chargement avec animation
 */
export const ChargementMessage = () => (
  <div className="flex items-center space-x-3 p-4 bg-gray-800/50 rounded-lg border border-gray-600/30">
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
    </div>
    <span className="text-gray-300 text-sm">L'assistant réfléchit...</span>
  </div>
);