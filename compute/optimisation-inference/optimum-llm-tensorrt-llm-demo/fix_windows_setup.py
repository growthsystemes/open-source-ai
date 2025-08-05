#!/usr/bin/env python3
"""
Script de correction pour les problèmes Windows spécifiques.

Corrige les problèmes PyTorch et de dépendances sur Windows.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def check_visual_cpp():
    """Vérifie et guide pour Visual C++ Redistributables."""
    print("🔍 Vérification Visual C++ Redistributables...")
    
    # Test simple d'import qui échoue souvent sans VC++
    try:
        import ctypes
        # Test de base des DLL système
        kernel32 = ctypes.windll.kernel32
        print("✅ DLL système OK")
        return True
    except Exception:
        print("❌ Problème DLL système détecté")
        print("📋 Action requise : Installez Visual C++ Redistributables")
        print("   Téléchargez : https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False


def fix_pytorch_windows():
    """Correction spécifique PyTorch Windows."""
    print("🔧 Correction PyTorch pour Windows...")
    
    commands = [
        # Nettoyage cache pip
        ([sys.executable, "-m", "pip", "cache", "purge"], "Nettoyage cache pip"),
        
        # Désinstallation PyTorch
        ([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"], 
         "Désinstallation PyTorch"),
        
        # Installation PyTorch CPU (plus stable sur Windows)
        ([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
          "--index-url", "https://download.pytorch.org/whl/cpu"], 
         "Installation PyTorch CPU"),
    ]
    
    for cmd, desc in commands:
        print(f"🔄 {desc}...")
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {desc} - OK")
            else:
                print(f"⚠️  {desc} - Avertissement")
                if result.stderr:
                    print(f"   Détail: {result.stderr.strip()[:100]}")
        except Exception as e:
            print(f"❌ {desc} - Erreur: {e}")


def fix_path_issues():
    """Correction des problèmes de PATH Windows."""
    print("🔧 Vérification PATH...")
    
    # Chemin Scripts Python utilisateur
    user_scripts = Path.home() / "AppData" / "Roaming" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts"
    
    current_path = os.environ.get("PATH", "")
    
    if str(user_scripts) not in current_path:
        print(f"⚠️  Scripts Python pas dans PATH: {user_scripts}")
        print("📋 Pour corriger définitivement, ajoutez à votre PATH système :")
        print(f"   {user_scripts}")
        
        # Ajout temporaire pour cette session
        os.environ["PATH"] = f"{user_scripts};{current_path}"
        print("✅ PATH temporaire ajusté pour cette session")
    else:
        print("✅ PATH Scripts Python OK")


def test_basic_imports():
    """Test des imports de base avec gestion d'erreur."""
    print("🧪 Test des imports critiques...")
    
    # Test sans PyTorch d'abord
    try:
        import numpy
        print("✅ NumPy OK")
    except Exception as e:
        print(f"❌ NumPy échec: {e}")
        return False
    
    try:
        import transformers
        print("✅ Transformers OK")
    except Exception as e:
        print(f"❌ Transformers échec: {e}")
        return False
    
    # Test PyTorch en dernier
    try:
        import torch
        print(f"✅ PyTorch OK (version: {torch.__version__})")
        print(f"   CUDA disponible: {torch.cuda.is_available()}")
        return True
    except Exception as e:
        print(f"❌ PyTorch échec: {e}")
        return False


def create_windows_env():
    """Crée un .env adapté Windows."""
    print("🔧 Configuration .env pour Windows...")
    
    env_content = """# Configuration Windows pour inference-optim-llm
MODEL_ID=gpt2
BATCH_SIZE=1
MAX_NEW_TOKENS=32
CUDA_VISIBLE_DEVICES=0

# Cache Windows
HF_HOME=C:/Users/%USERNAME%/.cache/huggingface

# Configuration CPU (plus stable sur Windows)
TORCH_DEVICE=cpu
"""
    
    env_file = Path(".env")
    env_file.write_text(env_content, encoding="utf-8")
    print("✅ Fichier .env créé (config CPU Windows)")


def test_cli_basic():
    """Test CLI basique sans dépendances lourdes."""
    print("🧪 Test CLI basique...")
    
    try:
        # Test import du module CLI sans exécution
        import importlib.util
        
        cli_path = Path(__file__).parent / "inference_optim_llm" / "cli.py"
        if not cli_path.exists():
            print("❌ Fichier CLI introuvable")
            return False
        
        # Test d'aide avec timeout court
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.insert(0, '.'); "
            "try: from inference_optim_llm.cli import app; print('CLI_OK')\n"
            "except Exception as e: print(f'CLI_ERROR: {e}')"
        ], capture_output=True, text=True, timeout=10)
        
        if "CLI_OK" in result.stdout:
            print("✅ CLI importable")
            return True
        else:
            print(f"❌ CLI non importable: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test CLI: {e}")
        return False


def main():
    """Point d'entrée principal."""
    print("🔧 Correction des problèmes Windows - inference-optim-llm")
    print("=" * 65)
    
    # 1. Vérification Visual C++
    check_visual_cpp()
    
    # 2. Correction PATH
    fix_path_issues()
    
    # 3. Correction PyTorch
    fix_pytorch_windows()
    
    # 4. Test imports
    imports_ok = test_basic_imports()
    
    # 5. Configuration environnement
    create_windows_env()
    
    # 6. Test CLI basique
    cli_ok = test_cli_basic()
    
    print("\n" + "=" * 65)
    if imports_ok and cli_ok:
        print("🎉 Corrections appliquées avec succès !")
        print("\n📝 Prochaines étapes :")
        print("   1. Redémarrez votre terminal PowerShell")
        print("   2. Testez: python -c \"import torch; print('PyTorch OK')\"")
        print("   3. Testez: python scripts/validate_setup.py")
        print("   4. Si problème persiste: Installez VC++ Redistributables")
    else:
        print("❌ Problèmes détectés - Actions requises :")
        if not imports_ok:
            print("   - Installez Visual C++ Redistributables 2015-2022")
            print("   - Redémarrez et relancez ce script")
        if not cli_ok:
            print("   - Vérifiez l'installation du package: pip install -e .")
    
    print(f"\n💡 En cas de problème persistant :")
    print("   - Utilisez un environnement conda/venv dédié")
    print("   - Installez PyTorch via conda : conda install pytorch cpuonly -c pytorch")


if __name__ == "__main__":
    main()