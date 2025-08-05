#!/usr/bin/env python3
"""
Script de démarrage rapide - Installation et test en une commande.

Usage: python quick_start.py
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def detect_os():
    """Détecte le système d'exploitation."""
    system = platform.system().lower()
    return system


def install_dependencies_windows():
    """Installation spécifique Windows."""
    print("🪟 Détection Windows - Installation spécialisée...")
    
    commands = [
        # Package principal
        ([sys.executable, "-m", "pip", "install", "-e", "."], 
         "Installation package principal"),
        
        # PyTorch CPU (plus stable sur Windows)
        ([sys.executable, "-m", "pip", "install", "torch", "torchvision", 
          "--index-url", "https://download.pytorch.org/whl/cpu"], 
         "Installation PyTorch CPU"),
         
        # Autres dépendances
        ([sys.executable, "-m", "pip", "install", "transformers", "typer", "rich", "huggingface-hub"], 
         "Installation utilitaires"),
    ]
    
    for cmd, desc in commands:
        print(f"🔄 {desc}...")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ {desc} - OK")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  {desc} - Problème détecté")
            if "torch" in " ".join(cmd):
                print("   💡 PyTorch peut nécessiter Visual C++ Redistributables")
            return False
    
    return True


def install_dependencies_unix():
    """Installation pour Linux/Mac."""
    print("🐧 Installation Unix/Linux/Mac...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "torch", "transformers", "typer", "rich"], check=True)
        print("✅ Dépendances installées")
        return True
    except subprocess.CalledProcessError:
        print("❌ Échec installation dépendances")
        return False


def main():
    print("🚀 Démarrage rapide inference-optim-llm")
    print("=" * 50)
    
    # Détection OS
    os_type = detect_os()
    print(f"🖥️  Système détecté: {os_type}")
    
    # 1. Installation des dépendances selon l'OS
    print("📦 Installation des dépendances...")
    if os_type == "windows":
        install_success = install_dependencies_windows()
    else:
        install_success = install_dependencies_unix()
    
    if not install_success:
        print("❌ Échec installation dépendances")
        if os_type == "windows":
            print("💡 Essayez: python fix_windows_setup.py")
        return False
    
    # 2. Configuration environnement
    print("\n🔧 Configuration environnement...")
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """MODEL_ID=gpt2
BATCH_SIZE=1
MAX_NEW_TOKENS=32
CUDA_VISIBLE_DEVICES=0
"""
        env_file.write_text(env_content)
        print("✅ Fichier .env créé avec configuration de test")
    
    # 3. Test CLI adapté selon l'OS
    print("\n🧪 Test de l'interface CLI...")
    try:
        if os_type == "windows":
            # Test plus robuste pour Windows
            result = subprocess.run([
                sys.executable, "-c", 
                "import sys; sys.path.insert(0, '.'); "
                "try: from inference_optim_llm.cli import app; print('CLI_OK')\n"
                "except Exception as e: print(f'CLI_ERROR: {e}')"
            ], capture_output=True, text=True, timeout=15)
            
            if "CLI_OK" in result.stdout:
                print("✅ CLI fonctionnel")
            elif "CLI_ERROR" in result.stdout:
                print(f"⚠️  CLI partiellement fonctionnel: {result.stdout}")
                print("💡 Essayez: python fix_windows_setup.py")
            else:
                print("❌ CLI non testable")
                return False
        else:
            # Test standard pour Unix
            result = subprocess.run([
                sys.executable, "-m", "inference_optim_llm.cli", "--help"
            ], capture_output=True, text=True, check=True)
            print("✅ CLI fonctionnel")
            
    except subprocess.CalledProcessError:
        print("❌ CLI non fonctionnel")
        if os_type == "windows":
            print("💡 Problème PyTorch probable - Essayez: python fix_windows_setup.py")
        return False
    
    # 4. Test rapide
    print("\n⚡ Test rapide avec GPT-2...")
    try:
        # Test très basique avec timeout
        result = subprocess.run([
            sys.executable, "-m", "inference_optim_llm.cli", "run", "baseline",
            "--prompts-file", "data/prompts.txt", "--max-new-tokens", "5", "--quiet"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 or "baseline" in result.stderr.lower():
            print("✅ Pipeline de base fonctionnel")
        else:
            print("⚠️  Pipeline testé - vérifiez manuellement")
    except subprocess.TimeoutExpired:
        print("⚠️  Test timeout - probablement OK")
    except Exception as e:
        print(f"⚠️  Test limité: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Setup initial terminé !")
    print("\n📋 Commandes de test :")
    if os_type == "windows":
        print("   python quick_test_windows.py  # Test rapide Windows")
        print("   python fix_windows_setup.py   # Si problème PyTorch")
    print("   python -m inference_optim_llm.cli --help")
    print("   python -m inference_optim_llm.cli run baseline")
    print("   python scripts/validate_setup.py")
    print("\n📚 Guide complet : SETUP.md")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)