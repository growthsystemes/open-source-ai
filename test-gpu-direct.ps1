# Test direct GPU avec Docker Desktop moderne

Write-Host "🧪 Test GPU avec Docker Desktop..." -ForegroundColor Blue

# Test 1: Images CUDA légères
$testImages = @(
    "nvidia/cuda:12.6-base-ubuntu22.04",
    "nvidia/cuda:12.2-base-ubuntu22.04", 
    "nvidia/cuda:11.8-base-ubuntu22.04"
)

$success = $false
foreach ($image in $testImages) {
    Write-Host "Test avec $image..." -ForegroundColor Yellow
    try {
        $result = docker run --rm --gpus all $image nvidia-smi
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SUCCESS! GPU fonctionne avec $image" -ForegroundColor Green
            $success = $true
            break
        }
    } catch {
        Write-Host "❌ Échec: $image" -ForegroundColor Red
    }
}

if ($success) {
    Write-Host "`n🎉 GPU FONCTIONNEL!" -ForegroundColor Green
    Write-Host "Docker Desktop supporte déjà votre RTX 4070" -ForegroundColor Green
    Write-Host "`nTest du projet:" -ForegroundColor Blue
    Write-Host "docker-compose --profile baseline up --build" -ForegroundColor White
} else {
    Write-Host "`n❌ GPU non accessible" -ForegroundColor Red
    Write-Host "Solutions alternatives:" -ForegroundColor Yellow
    Write-Host "1. Mode CPU (fonctionne parfaitement)" -ForegroundColor White
    Write-Host "2. Image Docker avec GPU pré-configuré" -ForegroundColor White
}