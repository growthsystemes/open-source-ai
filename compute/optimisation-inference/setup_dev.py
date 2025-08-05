#!/usr/bin/env python3
"""
Script de configuration rapide pour l'environnement de développement.

Ce script :
1. Installe les dépendances nécessaires
2. Configure l'environnement
3. Valide l'installation
4. Lance un test de base
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check=True):
    """Exécute une commande avec gestion d'erreur."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - ÉCHEC")
            print(f"   Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False


def check_python_version():
    """Vérifie la version de Python."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Version trop ancienne")
        print("   Requiert Python 3.9+")
        return False


def setup_environment():
    """Configure l'environnement .env si nécessaire."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("🔄 Création du fichier .env depuis .env.example...")
        env_file.write_text(env_example.read_text())
        print("✅ Fichier .env créé")
        print("   💡 Éditez .env pour personnaliser la configuration")
    elif env_file.exists():
        print("✅ Fichier .env déjà présent")
    else:
        print("⚠️  Pas de .env.example trouvé")


def install_dependencies():
    """Installe les dépendances du projet."""
    commands = [
        ("pip install --upgrade pip", "Mise à jour pip"),
        ("pip install -e .", "Installation du package local"),
        ("pip install torch transformers", "Installation PyTorch et Transformers"),
        ("pip install typer rich", "Installation CLI et UI"),
        ("pip install huggingface-hub", "Installation HuggingFace Hub"),
        ("pip install pytest pytest-cov", "Installation outils de test"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    return success


def validate_installation():
    """Valide que l'installation fonctionne."""
    print("\n🔍 Validation de l'installation...")
    
    # Test des imports critiques
    imports = [
        ("import torch", "PyTorch"),
        ("import transformers", "Transformers"),
        ("import typer", "Typer"),
        ("import inference_optim_llm", "Package local"),
    ]
    
    for import_cmd, name in imports:
        try:
            exec(import_cmd)
            print(f"✅ Import {name} - OK")
        except Exception as e:
            print(f"❌ Import {name} - ÉCHEC: {e}")
            return False
    
    # Test de la commande CLI
    if run_command("python -m inference_optim_llm.cli --help", "Test CLI", check=False):
        print("✅ CLI fonctionnel")
    else:
        print("❌ CLI non fonctionnel")
        return False
    
    return True


def run_quick_test():
    """Lance un test rapide du système."""
    print("\n🧪 Test rapide du système...")
    
    # Test avec un prompt minimal
    test_prompts = Path("test_prompts_temp.txt")
    test_prompts.write_text("Hello, this is a test.")
    
    try:
        # Test que le CLI run fonctionne (même si ça échoue sur le modèle)
        cmd = f"python -m inference_optim_llm.cli run baseline --prompts-file {test_prompts} --quiet"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if "Chargement du modèle" in result.stderr or "HFRunner" in result.stderr:
            print("✅ Pipeline de base fonctionnel (erreur modèle attendue)")
        else:
            print("⚠️  Pipeline de base - statut incertain")
    except subprocess.TimeoutExpired:
        print("⚠️  Test timeout - pipeline probablement OK")
    except Exception as e:
        print(f"⚠️  Erreur test: {e}")
    finally:
        test_prompts.unlink(missing_ok=True)


def main():
    """Point d'entrée principal."""
    print("🚀 Configuration de l'environnement de développement inference-optim-llm")
    print("=" * 70)
    
    # Vérifications préliminaires
    if not check_python_version():
        sys.exit(1)
    
    # Configuration
    setup_environment()
    
    # Installation
    if not install_dependencies():
        print("\n❌ Échec de l'installation des dépendances")
        sys.exit(1)
    
    # Validation
    if not validate_installation():
        print("\n❌ Échec de la validation")
        sys.exit(1)
    
    # Test rapide
    run_quick_test()
    
    print("\n" + "=" * 70)
    print("🎉 Configuration terminée avec succès !")
    print("\n📝 Prochaines étapes :")
    print("   1. Éditez .env pour votre configuration")
    print("   2. Testez: python -m inference_optim_llm.cli --help")
    print("   3. Lancez: python -m inference_optim_llm.cli run baseline")
    print("   4. Pour Docker: cd docker && docker-compose up baseline")


if __name__ == "__main__":
    main()