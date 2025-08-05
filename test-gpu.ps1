# Script PowerShell pour tester l'accès GPU avec Docker

Write-Host "🧪 Test d'accès GPU avec Docker..." -ForegroundColor Blue

# Test 1: Vérifier nvidia-smi sur l'hôte
Write-Host "`n1. Test nvidia-smi sur l'hôte:" -ForegroundColor Yellow
try {
    nvidia-smi
    Write-Host "✅ GPU détecté sur l'hôte" -ForegroundColor Green
} catch {
    Write-Host "❌ nvidia-smi échoué sur l'hôte" -ForegroundColor Red
    Write-Host "💡 Installez les pilotes NVIDIA" -ForegroundColor Yellow
    exit 1
}

# Test 2: Vérifier que Docker Desktop supporte GPU
Write-Host "`n2. Test Docker + GPU:" -ForegroundColor Yellow
$testImage = "nvidia/cuda:12.0-base-ubuntu20.04"

# Essayer avec une image CUDA plus récente
Write-Host "Téléchargement image CUDA de test..." -ForegroundColor Cyan
docker pull $testImage

if ($LASTEXITCODE -eq 0) {
    Write-Host "Test d'accès GPU dans Docker..." -ForegroundColor Cyan
    docker run --rm --gpus all $testImage nvidia-smi
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GPU accessible via Docker !" -ForegroundColor Green
        Write-Host "`n🚀 Vous pouvez maintenant lancer:" -ForegroundColor Blue
        Write-Host "docker-compose --profile baseline up --build" -ForegroundColor White
    } else {
        Write-Host "❌ GPU non accessible via Docker" -ForegroundColor Red
        Write-Host "💡 Vérifiez NVIDIA Container Toolkit" -ForegroundColor Yellow
        Write-Host "https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Échec téléchargement image CUDA" -ForegroundColor Red
    Write-Host "💡 Essayons sans GPU..." -ForegroundColor Yellow
    
    # Modifier .env pour CPU seulement
    Write-Host "`nConfiguration CPU pour test:" -ForegroundColor Cyan
    (Get-Content .env) -replace 'CUDA_VISIBLE_DEVICES=0', 'CUDA_VISIBLE_DEVICES=""' | Set-Content .env
    Write-Host "✅ Configuration CPU activée" -ForegroundColor Green
}

Write-Host "`n📋 Commandes de test:" -ForegroundColor Blue
Write-Host "- GPU: docker-compose --profile baseline up --build" -ForegroundColor White
Write-Host "- CPU: Modifiez .env avec CUDA_VISIBLE_DEVICES=`"`"" -ForegroundColor White