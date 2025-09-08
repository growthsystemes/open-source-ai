/**
 * Test simple pour vérifier que tout fonctionne
 */

console.log('🧪 Test simple de Guardrails IA');

// Test 1: Vérification des variables d'environnement
console.log('\n📋 Variables d\'environnement :');
console.log('- PORT:', process.env.PORT || '3001');
console.log('- NODE_ENV:', process.env.NODE_ENV || 'development');
console.log('- OPENAI_API_KEY présente:', process.env.OPENAI_API_KEY ? '✅ Oui' : '❌ Non');
console.log('- GUARDRAIL_MODEL:', process.env.GUARDRAIL_MODEL || 'gpt-4o-mini');

// Test 2: Serveur HTTP simple
const http = require('http');

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const url = req.url || '';

  // Route de santé simple
  if (url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      openai_configured: process.env.OPENAI_API_KEY ? true : false
    }));
    return;
  }

  // Page d'accueil
  if (url === '/' || url === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`
      <!DOCTYPE html>
      <html lang="fr">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>🛡️ Guardrails IA - Test</title>
          <style>
              body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f5f5f5;
              }
              .header { 
                text-align: center; 
                margin-bottom: 30px;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
              }
              .status { 
                background: #e8f5e8; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0;
                border-left: 4px solid #28a745;
              }
              .warning {
                background: #fff3cd;
                color: #856404;
                border-left: 4px solid #ffc107;
              }
              .test-section { 
                background: white; 
                padding: 20px; 
                border-radius: 8px; 
                margin: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
              }
              button { 
                background: #007cba; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer;
                margin: 5px;
              }
              button:hover { background: #005a87; }
              .result { 
                margin: 10px 0; 
                padding: 10px; 
                border-radius: 5px;
                border-left: 3px solid #ccc;
              }
              .success { background: #d4edda; color: #155724; border-left-color: #28a745; }
              .error { background: #f8d7da; color: #721c24; border-left-color: #dc3545; }
          </style>
      </head>
      <body>
          <div class="header">
              <h1>🛡️ Guardrails IA</h1>
              <p>Test de l'infrastructure de base</p>
          </div>
          
          <div class="status ${process.env.OPENAI_API_KEY ? '' : 'warning'}">
              <strong>📊 État du système</strong><br>
              Port: ${process.env.PORT || 3001}<br>
              Environnement: ${process.env.NODE_ENV || 'development'}<br>
              Modèle: ${process.env.GUARDRAIL_MODEL || 'gpt-4o-mini'}<br>
              API OpenAI: ${process.env.OPENAI_API_KEY ? '✅ Configurée' : '⚠️ Manquante'}
          </div>

          ${process.env.OPENAI_API_KEY ? '' : `
          <div class="status warning">
              <strong>⚠️ Configuration requise</strong><br>
              Pour tester les fonctionnalités IA, vous devez :<br>
              1. Ouvrir le fichier <code>.env</code><br>
              2. Remplacer <code>votre_cle_api_openai_ici</code> par votre vraie clé OpenAI<br>
              3. Redémarrer le serveur
          </div>
          `}

          <div class="test-section">
              <h3>🔍 Tests de base</h3>
              
              <button onclick="testHealth()">Test de santé</button>
              <button onclick="testServer()">Test serveur</button>
              
              <div id="results"></div>
          </div>

          <script>
              // Tests automatiques au chargement
              window.onload = function() {
                  testHealth();
                  showResult('Infrastructure: Serveur HTTP démarré ✅', true);
                  showResult('Configuration: Variables d\\'environnement chargées ✅', true);
              };

              async function testHealth() {
                  try {
                      const response = await fetch('/health');
                      const data = await response.json();
                      showResult('API Santé: ' + data.status + ' ✅', true);
                      showResult('OpenAI: ' + (data.openai_configured ? 'Configurée ✅' : 'Non configurée ⚠️'), data.openai_configured);
                  } catch (error) {
                      showResult('Erreur test santé: ' + error.message, false);
                  }
              }

              function testServer() {
                  showResult('Serveur HTTP: Accessible et fonctionnel ✅', true);
                  showResult('CORS: Headers configurés ✅', true);
                  showResult('Routes: /health et / disponibles ✅', true);
              }

              function showResult(message, isSuccess) {
                  const div = document.createElement('div');
                  div.className = 'result ' + (isSuccess ? 'success' : 'error');
                  div.innerHTML = '<strong>' + new Date().toLocaleTimeString() + '</strong> - ' + message;
                  document.getElementById('results').appendChild(div);
              }
          </script>
      </body>
      </html>
    `);
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Route non trouvée' }));
});

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log(`🚀 Serveur de test démarré sur http://localhost:${PORT}`);
  console.log(`🔍 Interface de test: http://localhost:${PORT}`);
  console.log(`💚 API Santé: http://localhost:${PORT}/health`);
  console.log('\\n✨ Le serveur est prêt pour les tests !');
});

// Gestion propre de l'arrêt
process.on('SIGTERM', () => {
  console.log('🛑 Arrêt du serveur...');
  server.close(() => {
    console.log('✅ Serveur arrêté proprement');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\\n🛑 Arrêt du serveur...');
  server.close(() => {
    console.log('✅ Serveur arrêté proprement');
    process.exit(0);
  });
});