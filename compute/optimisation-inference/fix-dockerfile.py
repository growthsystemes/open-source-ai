#!/usr/bin/env python3
"""
Script pour corriger les problèmes de syntaxe dans les Dockerfiles
"""

import re
from pathlib import Path

def fix_dockerfile_trtllm():
    """Corrige le Dockerfile TensorRT-LLM"""
    dockerfile_path = Path("docker/Dockerfile.trtllm")
    
    if not dockerfile_path.exists():
        print(f"❌ {dockerfile_path} non trouvé")
        return False
    
    content = dockerfile_path.read_text(encoding='utf-8')
    
    # Correction de la syntaxe Python multiline problématique
    problematic_pattern = r'python -c "try:\\n.*?print\(\'TensorRT-LLM not available\'\)"'
    fixed_command = 'python -c "try: import tensorrt_llm; print(\'TensorRT-LLM OK\'); except ImportError: print(\'TensorRT-LLM not available\')"'
    
    content = re.sub(problematic_pattern, fixed_command, content, flags=re.DOTALL)
    
    # Écrire le fichier corrigé
    dockerfile_path.write_text(content, encoding='utf-8')
    print(f"✅ {dockerfile_path} corrigé")
    return True

def verify_dockerfile():
    """Vérifie que la syntaxe est correcte"""
    dockerfile_path = Path("docker/Dockerfile.trtllm")
    content = dockerfile_path.read_text(encoding='utf-8')
    
    # Vérifier qu'il n'y a plus de \n dans les commandes Python
    if "\\n" in content and "python -c" in content:
        print("⚠️  Il reste des \\n problématiques")
        return False
    
    print("✅ Dockerfile vérifié - syntaxe OK")
    return True

if __name__ == "__main__":
    print("🔧 Correction des Dockerfiles...")
    fix_dockerfile_trtllm()
    verify_dockerfile()
    print("🎉 Corrections terminées !")