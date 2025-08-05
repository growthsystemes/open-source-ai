# Script d'installation NVIDIA Container Toolkit pour Windows
# Permet d'utiliser GPU NVIDIA avec Docker Desktop

Write-Host "🚀 Installation NVIDIA Container Toolkit pour Windows" -ForegroundColor Blue
Write-Host "=" * 60 -ForegroundColor Blue

# Vérification prérequis
Write-Host "`n1️⃣ Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier GPU NVIDIA
Write-Host "🔍 Vérification GPU NVIDIA..." -ForegroundColor Cyan
try {
    $gpuInfo = nvidia-smi --query-gpu=name --format=csv,noheader,nounits
    Write-Host "✅ GPU détecté : $gpuInfo" -ForegroundColor Green
} catch {
    Write-Host "❌ nvidia-smi non trouvé. Installez les pilotes NVIDIA d'abord." -ForegroundColor Red
    exit 1
}

# Vérifier Docker Desktop
Write-Host "🔍 Vérification Docker Desktop..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker détecté : $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker non trouvé. Installez Docker Desktop d'abord." -ForegroundColor Red
    exit 1
}

# Vérifier WSL2
Write-Host "🔍 Vérification WSL2..." -ForegroundColor Cyan
try {
    $wslVersion = wsl --version
    Write-Host "✅ WSL2 disponible" -ForegroundColor Green
} catch {
    Write-Host "⚠️  WSL2 non détecté. Installation recommandée." -ForegroundColor Yellow
}

Write-Host "`n2️⃣ Configuration Docker Desktop..." -ForegroundColor Yellow
Write-Host "📋 Actions manuelles requises :" -ForegroundColor Cyan
Write-Host "1. Ouvrez Docker Desktop" -ForegroundColor White
Write-Host "2. Allez dans Settings > General" -ForegroundColor White
Write-Host "3. Activez 'Use the WSL 2 based engine'" -ForegroundColor White
Write-Host "4. Allez dans Settings > Resources > WSL Integration" -ForegroundColor White
Write-Host "5. Activez 'Enable integration with my default WSL distro'" -ForegroundColor White
Write-Host "6. Cliquez 'Apply & Restart'" -ForegroundColor White

$response = Read-Host "`nAvez-vous configuré Docker Desktop ? (y/n)"
if ($response -ne 'y') {
    Write-Host "⏸️  Configurez Docker Desktop puis relancez ce script." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n3️⃣ Installation NVIDIA Container Toolkit..." -ForegroundColor Yellow

# Méthode 1: Via WSL2 (recommandée pour Docker Desktop)
Write-Host "🔧 Installation via WSL2..." -ForegroundColor Cyan
$wslCommands = @"
# Update package list
sudo apt update

# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker || echo 'Docker restart via systemctl failed - will restart via Docker Desktop'
"@

Write-Host "🔄 Exécution des commandes d'installation dans WSL2..." -ForegroundColor Cyan
Write-Host "Commandes à exécuter :" -ForegroundColor Yellow
Write-Host $wslCommands -ForegroundColor Gray

# Exécuter dans WSL2
wsl bash -c $wslCommands

Write-Host "`n4️⃣ Redémarrage Docker Desktop..." -ForegroundColor Yellow
Write-Host "📋 Actions requises :" -ForegroundColor Cyan
Write-Host "1. Fermez Docker Desktop complètement" -ForegroundColor White
Write-Host "2. Relancez Docker Desktop" -ForegroundColor White
Write-Host "3. Attendez qu'il soit complètement démarré" -ForegroundColor White

$response = Read-Host "`nAvez-vous redémarré Docker Desktop ? (y/n)"
if ($response -ne 'y') {
    Write-Host "⏸️  Redémarrez Docker Desktop puis relancez ce script pour tester." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n5️⃣ Test de l'accès GPU..." -ForegroundColor Yellow
Write-Host "🧪 Test avec image CUDA..." -ForegroundColor Cyan

# Test avec plusieurs images CUDA
$cudaImages = @(
    "nvidia/cuda:12.2-base-ubuntu20.04",
    "nvidia/cuda:11.8-base-ubuntu20.04",
    "nvidia/cuda:12.0-base-ubuntu20.04"
)

$success = $false
foreach ($image in $cudaImages) {
    Write-Host "Tentative avec $image..." -ForegroundColor Gray
    try {
        docker run --rm --gpus all $image nvidia-smi
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SUCCESS! GPU accessible via Docker avec $image" -ForegroundColor Green
            $success = $true
            break
        }
    } catch {
        Write-Host "❌ Échec avec $image" -ForegroundColor Red
    }
}

if ($success) {
    Write-Host "`n🎉 INSTALLATION RÉUSSIE !" -ForegroundColor Green
    Write-Host "Votre GPU est maintenant accessible via Docker." -ForegroundColor Green
    Write-Host "`n📋 Commandes de test :" -ForegroundColor Blue
    Write-Host "docker-compose --profile baseline up --build" -ForegroundColor White
    Write-Host "docker-compose --profile bench up --build" -ForegroundColor White
} else {
    Write-Host "`n❌ INSTALLATION ÉCHOUÉE" -ForegroundColor Red
    Write-Host "💡 Solutions alternatives :" -ForegroundColor Yellow
    Write-Host "1. Vérifiez que Docker Desktop utilise WSL2" -ForegroundColor White
    Write-Host "2. Redémarrez complètement votre PC" -ForegroundColor White
    Write-Host "3. Essayez la configuration manuelle :" -ForegroundColor White
    Write-Host "   https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html" -ForegroundColor Cyan
}
"@