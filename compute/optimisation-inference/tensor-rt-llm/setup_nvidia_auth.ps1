# Script PowerShell simplifié pour configurer l'authentification NVIDIA NGC
param(
    [Parameter()]
    [string]$ApiKey = ""
)

Write-Host "🔐 Configuration NVIDIA NGC Registry" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Vérification Docker
Write-Host "🔍 Vérification de Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker trouvé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker non trouvé. Installez Docker Desktop." -ForegroundColor Red
    exit 1
}

# Demander la clé API si pas fournie
if ([string]::IsNullOrEmpty($ApiKey)) {
    Write-Host ""
    Write-Host "📋 Vous avez besoin d'une clé API NGC de NVIDIA" -ForegroundColor Cyan
    Write-Host "Si vous n'en avez pas encore :" -ForegroundColor White
    Write-Host "1. Aller sur https://ngc.nvidia.com" -ForegroundColor White
    Write-Host "2. Créer un compte (gratuit)" -ForegroundColor White
    Write-Host "3. Profile > Setup > Generate API Key" -ForegroundColor White
    Write-Host ""
    
    $ApiKey = Read-Host "🔑 Entrez votre clé API NGC (commence par nvapi-)"
    
    if ([string]::IsNullOrEmpty($ApiKey)) {
        Write-Host "❌ Clé API requise" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔑 Connexion au registry NVIDIA..." -ForegroundColor Yellow

# Connexion Docker avec les credentials
$username = '$oauthtoken'

try {
    # Utiliser docker login de manière sécurisée
    $ApiKey | docker login nvcr.io --username $username --password-stdin
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connexion réussie au registry NVIDIA !" -ForegroundColor Green
        
        # Test de téléchargement de l'image
        Write-Host ""
        Write-Host "🧪 Test de l'image TensorRT-LLM..." -ForegroundColor Yellow
        Write-Host "⏳ Téléchargement en cours (peut prendre plusieurs minutes pour la première fois)..." -ForegroundColor Cyan
        
        docker pull nvcr.io/nvidia/tensorrt-llm/devel:1.0.0rc6
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Image TensorRT-LLM téléchargée avec succès !" -ForegroundColor Green
            Write-Host ""
            Write-Host "🚀 Vous pouvez maintenant lancer le benchmark :" -ForegroundColor Cyan
            Write-Host "   .\run_benchmark.ps1 -Mode all" -ForegroundColor White
            Write-Host "   ou" -ForegroundColor Gray
            Write-Host "   docker-compose --profile auto up benchmark-full" -ForegroundColor White
        } else {
            Write-Host "⚠️  Image pas encore téléchargée, mais authentification OK" -ForegroundColor Yellow
            Write-Host "L'image se téléchargera automatiquement au premier lancement" -ForegroundColor White
        }
    } else {
        Write-Host "❌ Échec de la connexion" -ForegroundColor Red
        Write-Host "Vérifiez que votre clé API est correcte" -ForegroundColor White
        Write-Host "Elle doit commencer par 'nvapi-' et être obtenue sur https://ngc.nvidia.com" -ForegroundColor White
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors de la connexion: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎯 Configuration terminée !" -ForegroundColor Green