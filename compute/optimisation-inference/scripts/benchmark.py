#!/usr/bin/env python3
"""
Script d'analyse de benchmark amélioré.

Amélioration par rapport à la version originale :
- Recherche automatique des fichiers JSONL dans reports/
- Lecture des fichiers JSONL avec recalcul des statistiques
- Génération de benchmark_results.md avec rapport Markdown
- Support de multiples variantes
- Gestion robuste des erreurs
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import sys


def load_jsonl_metrics(file_path: Path) -> List[Dict[str, Any]]:
    """
    Charge les métriques depuis un fichier JSONL.
    
    Parameters
    ----------
    file_path : Path
        Chemin vers le fichier JSONL.
        
    Returns
    -------
    List[Dict[str, Any]]
        Liste des échantillons de métriques.
    """
    samples = []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    sample = json.loads(line)
                    samples.append(sample)
                except json.JSONDecodeError as e:
                    print(f"Erreur JSON ligne {line_num} dans {file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}", file=sys.stderr)
    
    return samples


def compute_statistics(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Recalcule les statistiques depuis les échantillons bruts.
    
    Parameters
    ----------
    samples : List[Dict[str, Any]]
        Échantillons de métriques.
        
    Returns
    -------
    Dict[str, Any]
        Statistiques calculées.
    """
    if not samples:
        return {"count": 0}
    
    # Extraction des valeurs
    latencies = [s["latency"] for s in samples if "latency" in s]
    tps_values = [s["tps"] for s in samples if "tps" in s and not (
        isinstance(s["tps"], float) and (s["tps"] != s["tps"])  # NaN check
    )]
    tokens = [s["tokens"] for s in samples if "tokens" in s]
    memory_values = [s["memory_mb"] for s in samples if "memory_mb" in s and not (
        isinstance(s["memory_mb"], float) and (s["memory_mb"] != s["memory_mb"])
    )]
    power_values = [s["power_w"] for s in samples if "power_w" in s and not (
        isinstance(s["power_w"], float) and (s["power_w"] != s["power_w"])
    )]
    
    def percentile(values: List[float], p: float) -> float:
        """Calcul de percentile simple."""
        if not values:
            return float("nan")
        sorted_vals = sorted(values)
        k = (len(sorted_vals) - 1) * p / 100
        f = int(k)
        c = f + 1
        if c >= len(sorted_vals):
            return sorted_vals[-1]
        return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])
    
    def safe_mean(values: List[float]) -> float:
        return statistics.mean(values) if values else float("nan")
    
    def safe_max(values: List[float]) -> float:
        return max(values) if values else float("nan")
    
    return {
        "count": len(samples),
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_mean": safe_mean(latencies),
        "latency_max": safe_max(latencies),
        "tps_p50": percentile(tps_values, 50),
        "tps_p95": percentile(tps_values, 95),
        "tps_mean": safe_mean(tps_values),
        "tokens_total": sum(tokens),
        "memory_max": safe_max(memory_values),
        "power_mean": safe_mean(power_values),
    }


def generate_markdown_report(results: Dict[str, Dict[str, Any]], output_file: Path) -> None:
    """
    Génère un rapport Markdown des résultats de benchmark.
    
    Parameters
    ----------
    results : Dict[str, Dict[str, Any]]
        Résultats par variante.
    output_file : Path
        Fichier de sortie Markdown.
    """
    content = ["# Rapport de Benchmark", ""]
    content.append(f"*Généré automatiquement le {Path().cwd()}*")
    content.append("")
    
    # Tableau de comparaison
    content.append("## Comparaison des Performances")
    content.append("")
    content.append("| Variante | Échantillons | Latence P50 (s) | Latence P95 (s) | Débit P50 (tok/s) | Mémoire Max (MiB) | Puissance Moy (W) |")
    content.append("|----------|-------------|------------------|------------------|-------------------|-------------------|-------------------|")
    
    for variant, stats in results.items():
        count = stats.get("count", 0)
        lat_p50 = stats.get("latency_p50", float("nan"))
        lat_p95 = stats.get("latency_p95", float("nan"))
        tps_p50 = stats.get("tps_p50", float("nan"))
        mem_max = stats.get("memory_max", float("nan"))
        pow_mean = stats.get("power_mean", float("nan"))
        
        content.append(f"| {variant} | {count} | {lat_p50:.3f} | {lat_p95:.3f} | {tps_p50:.1f} | {mem_max:.0f} | {pow_mean:.1f} |")
    
    content.append("")
    
    # Calcul d'accélération si baseline et trtllm présents
    if "baseline" in results and "trtllm" in results:
        baseline_p50 = results["baseline"].get("latency_p50", 0)
        trtllm_p50 = results["trtllm"].get("latency_p50", 0)
        
        if baseline_p50 > 0 and trtllm_p50 > 0:
            speedup = baseline_p50 / trtllm_p50
            content.append(f"## Accélération")
            content.append("")
            content.append(f"**TensorRT-LLM vs Baseline**: {speedup:.2f}x plus rapide")
            content.append("")
    
    # Détails par variante
    content.append("## Détails par Variante")
    content.append("")
    
    for variant, stats in results.items():
        content.append(f"### {variant.title()}")
        content.append("")
        content.append(f"- **Échantillons**: {stats.get('count', 0)}")
        content.append(f"- **Latence moyenne**: {stats.get('latency_mean', float('nan')):.3f}s")
        content.append(f"- **Latence max**: {stats.get('latency_max', float('nan')):.3f}s")
        content.append(f"- **Débit moyen**: {stats.get('tps_mean', float('nan')):.1f} tok/s")
        content.append(f"- **Tokens total**: {stats.get('tokens_total', 0)}")
        content.append("")
    
    # Sauvegarde
    output_file.write_text("\n".join(content), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyse les résultats de benchmark et génère des rapports"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default="reports",
        help="Répertoire contenant les fichiers JSONL"
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default="reports/benchmark_comparison.csv",
        help="Fichier CSV de sortie"
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default="reports/benchmark_results.md",
        help="Fichier Markdown de sortie"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Mode silencieux"
    )
    
    args = parser.parse_args()
    
    # Création du répertoire de sortie
    args.reports_dir.mkdir(exist_ok=True)
    
    # Recherche automatique des fichiers JSONL
    jsonl_files = list(args.reports_dir.glob("*.jsonl"))
    if not jsonl_files:
        print(f"Aucun fichier JSONL trouvé dans {args.reports_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"📊 Analyse de {len(jsonl_files)} fichiers JSONL:")
        for f in jsonl_files:
            print(f"  - {f.name}")
    
    # Chargement et analyse des résultats
    results = {}
    for jsonl_file in jsonl_files:
        variant = jsonl_file.stem  # nom sans extension
        if not args.quiet:
            print(f"Traitement {variant}...")
        
        samples = load_jsonl_metrics(jsonl_file)
        if samples:
            stats = compute_statistics(samples)
            results[variant] = stats
            if not args.quiet:
                print(f"  {stats['count']} échantillons, latence P50: {stats.get('latency_p50', 'N/A'):.3f}s")
        else:
            print(f"  Aucun échantillon valide dans {jsonl_file}", file=sys.stderr)
    
    if not results:
        print("Aucune donnée valide trouvée", file=sys.stderr)
        sys.exit(1)
    
    # Génération du CSV
    if not args.quiet:
        print(f"💾 Génération CSV: {args.output_csv}")
    
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    import csv
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "variant", "count", "latency_p50", "latency_p95", "latency_mean",
            "tps_p50", "tps_mean", "memory_max", "power_mean"
        ])
        
        for variant, stats in results.items():
            writer.writerow([
                variant,
                stats.get("count", 0),
                stats.get("latency_p50", ""),
                stats.get("latency_p95", ""),
                stats.get("latency_mean", ""),
                stats.get("tps_p50", ""),
                stats.get("tps_mean", ""),
                stats.get("memory_max", ""),
                stats.get("power_mean", ""),
            ])
    
    # Génération du Markdown
    if not args.quiet:
        print(f"📝 Génération Markdown: {args.output_md}")
    
    generate_markdown_report(results, args.output_md)
    
    # Affichage du résumé
    if not args.quiet:
        print("\n🎯 Résumé des performances:")
        for variant, stats in results.items():
            lat_p50 = stats.get("latency_p50", float("nan"))
            tps_p50 = stats.get("tps_p50", float("nan"))
            print(f"  {variant}: {lat_p50:.3f}s latence, {tps_p50:.1f} tok/s")
        
        print("✅ Analyse terminée!")


if __name__ == "__main__":
    main()
