#!/usr/bin/env python3
"""
Script de téléchargement de modèles HuggingFace.

Compatible avec l'utilisation dans les Dockerfiles et en standalone.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("Erreur: huggingface_hub non installé", file=sys.stderr)
    print("Installez avec: pip install huggingface_hub", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Télécharge un modèle depuis HuggingFace Hub"
    )
    parser.add_argument(
        "--model_id", 
        "--model-id",
        required=True,
        help="ID du modèle HuggingFace (ex: meta-llama/Llama-2-7b-chat-hf)"
    )
    parser.add_argument(
        "--output_dir",
        "--output-dir", 
        help="Répertoire de destination (défaut: HF_HOME ou /workspace/models)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Reprendre un téléchargement interrompu (défaut: activé)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Mode silencieux"
    )
    
    args = parser.parse_args()
    
    # Détermination du répertoire de destination
    if args.output_dir:
        local_dir = args.output_dir
    else:
        # Priorité: HF_HOME > /workspace/models > ~/.cache/huggingface
        local_dir = os.environ.get(
            'HF_HOME', 
            '/workspace/models' if Path('/workspace').exists() 
            else str(Path.home() / '.cache' / 'huggingface' / 'models')
        )
    
    local_dir = Path(local_dir)
    
    if not args.quiet:
        print(f"📥 Téléchargement de {args.model_id}")
        print(f"📁 Destination: {local_dir}")
    
    try:
        # Création du répertoire si nécessaire
        local_dir.mkdir(parents=True, exist_ok=True)
        
        # Téléchargement du modèle
        downloaded_path = snapshot_download(
            args.model_id,
            local_dir=str(local_dir / args.model_id.replace('/', '--')),
            resume_download=args.resume,
        )
        
        if not args.quiet:
            print(f"✅ Téléchargement terminé: {downloaded_path}")
    
    except Exception as e:
        print(f"❌ Erreur de téléchargement: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
