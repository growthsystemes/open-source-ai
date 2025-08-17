# Script PowerShell pour lancer le benchmark TensorRT-LLM directement
Write-Host "🚀 Benchmark TensorRT-LLM - Lancement Direct" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Création des répertoires de données
Write-Host "📁 Création des répertoires..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\models", "data\engines", "data\checkpoints", "data\results" | Out-Null

# Variables
$IMAGE = "nvcr.io/nvidia/tensorrt-llm/devel:1.0.0rc6"
$PWD_UNIX = $PWD.Path.Replace('\', '/').Replace('C:', '/c')

Write-Host "🔧 Image: $IMAGE" -ForegroundColor Cyan
Write-Host "📂 Répertoire: $PWD" -ForegroundColor Cyan

# Lancement du benchmark complet
Write-Host ""
Write-Host "1️⃣  Construction du moteur TensorRT..." -ForegroundColor Yellow
docker run --rm --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 `
    -v "${PWD}:/workspace/host" `
    -w /workspace/host `
    $IMAGE /bin/bash scripts/build_engine.sh

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la construction du moteur" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2️⃣  Benchmark PyTorch (référence)..." -ForegroundColor Yellow
docker run --rm --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 `
    -v "${PWD}:/workspace/host" `
    -w /workspace/host `
    $IMAGE /bin/bash scripts/bench_pytorch.sh

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du benchmark PyTorch" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3️⃣  Benchmark TensorRT-LLM..." -ForegroundColor Yellow
docker run --rm --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 `
    -v "${PWD}:/workspace/host" `
    -w /workspace/host `
    $IMAGE /bin/bash scripts/bench_trt.sh

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du benchmark TensorRT" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "4️⃣  Comparaison des résultats..." -ForegroundColor Yellow
docker run --rm --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 `
    -v "${PWD}:/workspace/host" `
    -w /workspace/host `
    $IMAGE python3 scripts/compare.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la comparaison" -ForegroundColor Red
    exit 1
}

# Résultats
Write-Host ""
Write-Host "✅ BENCHMARK TERMINÉ !" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host "📊 Résultats disponibles dans .\data\results\" -ForegroundColor Cyan
Write-Host "   - pytorch_benchmark.json" -ForegroundColor White
Write-Host "   - tensorrt_benchmark.json" -ForegroundColor White
Write-Host "   - benchmark_comparison_report.json" -ForegroundColor White
Write-Host "   - benchmark_comparison.png" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Benchmark TensorRT-LLM vs PyTorch terminé avec succès !" -ForegroundColor Green
