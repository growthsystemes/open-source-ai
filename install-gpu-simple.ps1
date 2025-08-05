# Installation simple NVIDIA Container Toolkit pour Windows

Write-Host "🚀 Installation NVIDIA Container Toolkit" -ForegroundColor Blue

# Vérification GPU
Write-Host "1. Vérification GPU..." -ForegroundColor Yellow
nvidia-smi
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ GPU non détecté" -ForegroundColor Red
    exit 1
}

# Vérification Docker
Write-Host "2. Vérification Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker non détecté" -ForegroundColor Red
    exit 1
}

# Vérification WSL2
Write-Host "3. Vérification WSL2..." -ForegroundColor Yellow
wsl --version

Write-Host "4. Configuration Docker Desktop requise:" -ForegroundColor Yellow
Write-Host "   - Settings > General > Use WSL 2 based engine" -ForegroundColor White
Write-Host "   - Settings > Resources > WSL Integration > Enable integration" -ForegroundColor White
Write-Host "   - Apply & Restart" -ForegroundColor White

Write-Host "5. Installation dans WSL2:" -ForegroundColor Yellow
Write-Host "   wsl" -ForegroundColor White
Write-Host "   sudo apt update" -ForegroundColor White
Write-Host "   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg" -ForegroundColor White
Write-Host "   echo 'deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/deb/ /' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list" -ForegroundColor White
Write-Host "   sudo apt update && sudo apt install -y nvidia-container-toolkit" -ForegroundColor White
Write-Host "   sudo nvidia-ctk runtime configure --runtime=docker" -ForegroundColor White

Write-Host "6. Redémarrez Docker Desktop complètement" -ForegroundColor Yellow

Write-Host "7. Test:" -ForegroundColor Yellow
Write-Host "   docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu20.04 nvidia-smi" -ForegroundColor White