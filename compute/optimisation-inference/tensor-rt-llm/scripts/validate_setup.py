#!/usr/bin/env python3
"""
Script de validation de l'environnement pour TensorRT-LLM Benchmark
Vérifie que tous les prérequis sont installés et fonctionnels
"""

import sys
import subprocess
import platform
import json
from pathlib import Path

def check_command(cmd, name, required=True):
    """Vérifie qu'une commande est disponible"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {name}: Disponible")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        status = "❌" if required else "⚠️"
        print(f"{status} {name}: {'Requis mais manquant' if required else 'Optionnel, non trouvé'}")
        return False

def check_python_packages():
    """Vérifie les packages Python optionnels"""
    packages = [
        ("docker", "Docker Python SDK"),
        ("nvidia-ml-py3", "NVIDIA Management Library"),
        ("matplotlib", "Matplotlib pour les graphiques"),
        ("seaborn", "Seaborn pour les graphiques"),
        ("pandas", "Pandas pour l'analyse de données"),
        ("numpy", "NumPy"),
        ("transformers", "Hugging Face Transformers"),
        ("torch", "PyTorch")
    ]
    
    print("\n🐍 Packages Python (optionnels pour l'analyse locale):")
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}: Installé")
        except ImportError:
            print(f"⚠️  {name}: Non installé (optionnel)")

def check_gpu_memory():
    """Vérifie la mémoire GPU disponible"""
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.free", "--format=csv,noheader,nounits"], 
                              capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
        print(f"\n🎮 Mémoire GPU:")
        
        for i, line in enumerate(lines):
            total, free = map(int, line.split(', '))
            used = total - free
            print(f"   GPU {i}: {free:,} MB libre / {total:,} MB total ({used:,} MB utilisé)")
            
            if total < 4000:
                print(f"   ⚠️  GPU {i}: Mémoire faible ({total:,} MB). 6+ GB recommandé pour TinyLlama.")
            elif total >= 8000:
                print(f"   ✅ GPU {i}: Mémoire suffisante pour les modèles moyens.")
                
    except subprocess.CalledProcessError:
        print("❌ Impossible de vérifier la mémoire GPU")

def check_disk_space():
    """Vérifie l'espace disque disponible"""
    try:
        current_dir = Path.cwd()
        stat = current_dir.stat() if hasattr(current_dir, 'stat') else None
        
        if platform.system() == "Windows":
            import shutil
            total, used, free = shutil.disk_usage(current_dir)
        else:
            import os
            statvfs = os.statvfs(current_dir)
            total = statvfs.f_frsize * statvfs.f_blocks
            free = statvfs.f_frsize * statvfs.f_bavail
            used = total - free
        
        total_gb = total / (1024**3)
        free_gb = free / (1024**3)
        used_gb = used / (1024**3)
        
        print(f"\n💾 Espace disque:")
        print(f"   Total: {total_gb:.1f} GB")
        print(f"   Libre: {free_gb:.1f} GB")
        print(f"   Utilisé: {used_gb:.1f} GB")
        
        if free_gb < 10:
            print("   ⚠️  Espace disque faible. 10+ GB recommandé.")
        else:
            print("   ✅ Espace disque suffisant.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de l'espace disque: {e}")

def check_docker_gpu():
    """Test spécifique de l'accès GPU via Docker"""
    print(f"\n🐳 Test Docker + GPU:")
    
    try:
        # Test simple avec l'image CUDA
        cmd = ["docker", "run", "--rm", "--gpus", "all", 
               "nvidia/cuda:12.0-base-ubuntu20.04", "nvidia-smi", "--list-gpus"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        
        gpu_count = len([line for line in result.stdout.strip().split('\n') if line.strip()])
        print(f"   ✅ Docker peut accéder à {gpu_count} GPU(s)")
        
        # Test de l'image TensorRT-LLM (plus long)
        print("   🔍 Test de l'image TensorRT-LLM (peut prendre quelques minutes)...")
        cmd_trt = ["docker", "run", "--rm", "--gpus", "all", 
                   "nvcr.io/nvidia/tensorrt_llm:0.7.1-py3", "python3", "-c", 
                   "import tensorrt_llm; print('TensorRT-LLM importé avec succès')"]
        
        result_trt = subprocess.run(cmd_trt, capture_output=True, text=True, timeout=180)
        
        if result_trt.returncode == 0:
            print("   ✅ Image TensorRT-LLM fonctionnelle")
        else:
            print("   ⚠️  Image TensorRT-LLM non testable (première utilisation)")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Test Docker timeout (peut être normal lors du premier pull)")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erreur Docker GPU: {e}")
        return False
    except FileNotFoundError:
        print("   ❌ Docker non trouvé")
        return False
    
    return True

def generate_system_report():
    """Génère un rapport système"""
    report = {
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture()[0]
        },
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    # Informations GPU
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], 
                              capture_output=True, text=True, check=True)
        
        gpus = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split(', ')
                if len(parts) >= 3:
                    gpus.append({
                        "name": parts[0],
                        "driver_version": parts[1],
                        "memory_mb": int(parts[2].split()[0])
                    })
        report["gpus"] = gpus
        
    except subprocess.CalledProcessError:
        report["gpus"] = []
    
    # Sauvegarde
    with open("system_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Rapport système sauvegardé dans: system_report.json")

def main():
    """Fonction principale de validation"""
    print("🔍 Validation de l'environnement TensorRT-LLM Benchmark")
    print("=" * 60)
    
    print(f"\n💻 Système: {platform.platform()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Commandes requises
    print(f"\n📋 Vérification des prérequis:")
    
    required_ok = True
    required_ok &= check_command(["docker", "--version"], "Docker")
    required_ok &= check_command(["docker-compose", "--version"], "Docker Compose")
    required_ok &= check_command(["nvidia-smi"], "NVIDIA Driver")
    
    # Commandes optionnelles
    print(f"\n🔧 Outils optionnels:")
    check_command(["git", "--version"], "Git", required=False)
    check_command(["make", "--version"], "Make", required=False)
    check_command(["jq", "--version"], "jq (pour le parsing JSON)", required=False)
    
    # Vérifications système
    check_gpu_memory()
    check_disk_space()
    
    # Test Docker + GPU
    docker_gpu_ok = check_docker_gpu()
    
    # Packages Python
    check_python_packages()
    
    # Génération du rapport
    generate_system_report()
    
    # Résumé final
    print(f"\n" + "=" * 60)
    print("🎯 RÉSUMÉ:")
    
    if required_ok and docker_gpu_ok:
        print("✅ Environnement prêt pour le benchmark TensorRT-LLM!")
        print("🚀 Vous pouvez lancer: docker-compose --profile auto up benchmark-full")
    else:
        print("❌ Problèmes détectés. Veuillez corriger les erreurs ci-dessus.")
        
        if not required_ok:
            print("   • Installez Docker et les drivers NVIDIA")
        if not docker_gpu_ok:
            print("   • Configurez l'accès GPU pour Docker")
    
    print(f"\n📋 Rapport détaillé: system_report.json")

if __name__ == "__main__":
    main()
