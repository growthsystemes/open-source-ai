# Script PowerShell pour Windows - Benchmark TensorRT-LLM
param(
    [Parameter()]
    [ValidateSet("all", "build", "pytorch", "tensorrt", "compare", "interactive")]
    [string]$Mode = "all"
)

Write-Host "🚀 Benchmark TensorRT-LLM - Mode: $Mode" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Vérification des prérequis
Write-Host "🔍 Vérification de l'environnement..." -ForegroundColor Yellow

# Test Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker trouvé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker non trouvé. Veuillez installer Docker Desktop." -ForegroundColor Red
    exit 1
}

# Test NVIDIA GPU
try {
    nvidia-smi | Out-Null
    Write-Host "✅ GPU NVIDIA détecté" -ForegroundColor Green
} catch {
    Write-Host "❌ nvidia-smi non trouvé. Vérifiez les drivers NVIDIA." -ForegroundColor Red
    exit 1
}

# Test Docker GPU support
try {
    docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi | Out-Null
    Write-Host "✅ Support GPU Docker confirmé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker ne peut pas accéder au GPU. Vérifiez nvidia-docker." -ForegroundColor Red
    exit 1
}

# Création des répertoires
Write-Host "📁 Création des répertoires..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\models", "data\engines", "data\checkpoints", "data\results" | Out-Null

# Exécution selon le mode
switch ($Mode) {
    "all" {
        Write-Host "🔄 Exécution du pipeline complet..." -ForegroundColor Cyan
        
        Write-Host "1️⃣  Construction du moteur TensorRT..." -ForegroundColor Yellow
        docker-compose --profile build-only up build-engine
        if ($LASTEXITCODE -ne 0) { Write-Host "❌ Erreur construction moteur" -ForegroundColor Red; exit 1 }
        
        Write-Host "2️⃣  Benchmark PyTorch..." -ForegroundColor Yellow
        docker-compose --profile pytorch-only up benchmark-pytorch
        if ($LASTEXITCODE -ne 0) { Write-Host "❌ Erreur benchmark PyTorch" -ForegroundColor Red; exit 1 }
        
        Write-Host "3️⃣  Benchmark TensorRT..." -ForegroundColor Yellow
        docker-compose --profile tensorrt-only up benchmark-tensorrt
        if ($LASTEXITCODE -ne 0) { Write-Host "❌ Erreur benchmark TensorRT" -ForegroundColor Red; exit 1 }
        
        Write-Host "4️⃣  Comparaison..." -ForegroundColor Yellow
        docker-compose --profile compare-only up compare-results
        if ($LASTEXITCODE -ne 0) { Write-Host "❌ Erreur comparaison" -ForegroundColor Red; exit 1 }
    }
    "build" {
        Write-Host "🔧 Construction du moteur TensorRT..." -ForegroundColor Cyan
        docker-compose --profile build-only up build-engine
    }
    "pytorch" {
        Write-Host "🔥 Benchmark PyTorch..." -ForegroundColor Cyan
        docker-compose --profile pytorch-only up benchmark-pytorch
    }
    "tensorrt" {
        Write-Host "⚡ Benchmark TensorRT..." -ForegroundColor Cyan
        docker-compose --profile tensorrt-only up benchmark-tensorrt
    }
    "compare" {
        Write-Host "📊 Comparaison des résultats..." -ForegroundColor Cyan
        docker-compose --profile compare-only up compare-results
    }
    "interactive" {
        Write-Host "🖥️  Mode interactif..." -ForegroundColor Cyan
        docker-compose --profile manual run --rm tensorrt-llm-benchmark
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ TERMINÉ!" -ForegroundColor Green
    Write-Host "📊 Résultats dans: .\data\results\" -ForegroundColor Cyan
    Write-Host "   - pytorch_benchmark.json" -ForegroundColor White
    Write-Host "   - tensorrt_benchmark.json" -ForegroundColor White
    Write-Host "   - benchmark_comparison_report.json" -ForegroundColor White
    Write-Host "   - benchmark_comparison.png" -ForegroundColor White
} else {
    Write-Host "❌ Erreur lors de l'exécution" -ForegroundColor Red
}
