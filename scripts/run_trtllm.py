#!/usr/bin/env python3
"""
Script d'exécution TensorRT-LLM.

Amélioration par rapport à la version originale :
- Option --out pour sauvegarder en JSONL
- Support des paramètres de configuration
- Meilleure gestion des erreurs
"""

import argparse
import json
import sys
from pathlib import Path

from inference_optim_llm.engines.trt import TRTRunner
from inference_optim_llm.core.metrics import MetricsCollector


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exécution TensorRT-LLM optimisée"
    )
    parser.add_argument(
        "--prompts-file", 
        type=Path,
        default="data/prompts.txt",
        help="Fichier contenant les prompts (un par ligne)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Fichier de sortie JSONL (si non spécifié, affiche le résumé JSON)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Taille de batch"
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=64,
        help="Nombre maximum de tokens à générer"
    )
    parser.add_argument(
        "--precision",
        type=str,
        default="fp16",
        help="Précision de l'engine (fp16, int8, etc.)"
    )
    parser.add_argument(
        "--engine-path",
        type=Path,
        help="Chemin explicite vers l'engine TensorRT-LLM"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Mode silencieux (pas d'affichage du résumé)"
    )
    
    args = parser.parse_args()
    
    # Vérification du fichier de prompts
    if not args.prompts_file.exists():
        print(f"Erreur: Fichier de prompts introuvable: {args.prompts_file}", file=sys.stderr)
        sys.exit(1)
    
    # Chargement des prompts
    try:
        prompts = args.prompts_file.read_text(encoding="utf-8").strip().splitlines()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not prompts:
        print("Erreur: Aucun prompt trouvé dans le fichier", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"🚄 TensorRT-LLM: traitement de {len(prompts)} prompts")
    
    # Reset des métriques
    MetricsCollector.reset_all()
    
    # Initialisation du runner
    try:
        runner_kwargs = {
            "batch_size": args.batch_size,
            "max_new_tokens": args.max_new_tokens,
            "precision": args.precision,
        }
        if args.engine_path:
            runner_kwargs["engine_path"] = str(args.engine_path)
            
        runner = TRTRunner(**runner_kwargs)
    except Exception as e:
        print(f"Erreur d'initialisation: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Traitement des prompts
    try:
        for i, prompt in enumerate(prompts, 1):
            runner.generate(prompt)
            if not args.quiet and i % 10 == 0:
                print(f"  Traité {i}/{len(prompts)} prompts")
        
        if not args.quiet:
            print("✅ Traitement terminé")
        
    except Exception as e:
        print(f"Erreur durant le traitement: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Sortie des résultats
    if args.out:
        # Sauvegarde en JSONL
        try:
            output_path = runner.save_metrics(args.out)
            if not args.quiet:
                print(f"💾 Métriques sauvegardées: {output_path}")
        except Exception as e:
            print(f"Erreur de sauvegarde: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Affichage du résumé JSON
        summary = runner.metrics.summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
