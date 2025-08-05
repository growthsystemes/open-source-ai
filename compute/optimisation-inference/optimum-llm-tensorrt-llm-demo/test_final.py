#!/usr/bin/env python3
"""
Test final ultra-simple pour vérifier que tout fonctionne.

À exécuter APRÈS avoir corrigé les problèmes Windows.
"""

def test_step(step_name, test_func):
    """Exécute un test avec affichage clair."""
    print(f"🧪 {step_name}...", end=" ")
    try:
        result = test_func()
        if result:
            print("✅ OK")
            return True
        else:
            print("❌ ÉCHEC")
            return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False


def test_python_basic():
    """Test Python de base."""
    import json
    import pathlib
    return True


def test_torch():
    """Test PyTorch."""
    import torch
    x = torch.tensor([1.0, 2.0])
    return len(x) == 2


def test_package():
    """Test du package local."""
    from inference_optim_llm.core.metrics import MetricsCollector
    mc = MetricsCollector("test")
    mc.add("test", 1.0, 5)
    return mc.summary()["count"] == 1


def test_cli_import():
    """Test import CLI."""
    from inference_optim_llm.cli import app
    return app is not None


def test_prompts_file():
    """Test fichier prompts."""
    from pathlib import Path
    prompts_file = Path("data/prompts.txt")
    if prompts_file.exists():
        content = prompts_file.read_text()
        return len(content.strip()) > 10
    return False


def main():
    print("🚀 TEST FINAL - Vérification complète")
    print("=" * 45)
    
    tests = [
        ("Python standard", test_python_basic),
        ("PyTorch", test_torch),
        ("Package local", test_package),
        ("CLI import", test_cli_import),
        ("Fichier prompts", test_prompts_file),
    ]
    
    results = []
    for test_name, test_func in tests:
        results.append(test_step(test_name, test_func))
    
    success_count = sum(results)
    total_count = len(results)
    
    print("\n" + "=" * 45)
    print(f"📊 Résultat: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 PARFAIT ! Tout fonctionne.")
        print("\n📝 Commandes suggérées :")
        print("   python -m inference_optim_llm.cli --help")
        print("   python -m inference_optim_llm.cli run baseline --max-new-tokens 10")
        return True
    elif success_count >= 4:
        print("⚠️  Presque parfait - quelques détails à corriger")
        return True
    else:
        print("❌ Problèmes majeurs détectés")
        print("💡 Exécutez: python fix_windows_setup.py")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)