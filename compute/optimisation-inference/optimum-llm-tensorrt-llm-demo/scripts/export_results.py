#!/usr/bin/env python3
"""
Script de génération de graphiques et rapports visuels.

Fonctionnalités :
- Graphiques de latence P50/P95 avec matplotlib
- Comparaison visuelle des performances
- Mise à jour automatique de docs/results.md
- Export PNG et SVG
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import conditionnel de matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None  # type: ignore


def load_benchmark_results(reports_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Charge les résultats de benchmark depuis le répertoire reports.
    
    Parameters
    ----------
    reports_dir : Path
        Répertoire contenant benchmark_results.json.
        
    Returns
    -------
    Dict[str, Dict[str, Any]]
        Données de benchmark par variante.
    """
    results_file = reports_dir / "benchmark_results.json"
    
    if not results_file.exists():
        print(f"Fichier de résultats introuvable: {results_file}", file=sys.stderr)
        return {}
    
    try:
        with results_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Extraction des résultats par variante
        return data.get("results", {})
    
    except Exception as e:
        print(f"Erreur lors du chargement de {results_file}: {e}", file=sys.stderr)
        return {}


def create_latency_chart(results: Dict[str, Dict[str, Any]], output_file: Path) -> None:
    """
    Crée un graphique en barres comparant les latences P50/P95.
    
    Parameters
    ----------
    results : Dict[str, Dict[str, Any]]
        Résultats de benchmark par variante.
    output_file : Path
        Fichier de sortie pour le graphique.
    """
    if not HAS_MATPLOTLIB:
        print("matplotlib non disponible - graphiques ignorés", file=sys.stderr)
        return
    
    if not results:
        print("Aucune donnée disponible pour les graphiques", file=sys.stderr)
        return
    
    # Préparation des données
    variants = list(results.keys())
    latency_p50 = [results[v].get("latency_p50", 0) for v in variants]
    latency_p95 = [results[v].get("latency_p95", 0) for v in variants]
    
    # Création du graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = range(len(variants))
    width = 0.35
    
    bars1 = ax.bar([x - width/2 for x in x_pos], latency_p50, width, 
                   label='Latence P50', alpha=0.8, color='#1f77b4')
    bars2 = ax.bar([x + width/2 for x in x_pos], latency_p95, width,
                   label='Latence P95', alpha=0.8, color='#ff7f0e')
    
    # Personnalisation
    ax.set_xlabel('Variante')
    ax.set_ylabel('Latence (secondes)')
    ax.set_title('Comparaison des Latences - P50 vs P95')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([v.title() for v in variants])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Ajout des valeurs sur les barres
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height:.3f}s',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points de décalage vertical
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=9)
    
    autolabel(bars1)
    autolabel(bars2)
    
    plt.tight_layout()
    
    # Sauvegarde en PNG et SVG
    for ext in ['png', 'svg']:
        output_path = output_file.with_suffix(f'.{ext}')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Graphique sauvegardé: {output_path}")
    
    plt.close()


def create_throughput_chart(results: Dict[str, Dict[str, Any]], output_file: Path) -> None:
    """
    Crée un graphique de débit (tokens/seconde).
    
    Parameters
    ----------
    results : Dict[str, Dict[str, Any]]
        Résultats de benchmark par variante.
    output_file : Path
        Fichier de sortie pour le graphique.
    """
    if not HAS_MATPLOTLIB:
        return
    
    if not results:
        return
    
    # Préparation des données
    variants = list(results.keys())
    tps_p50 = [results[v].get("tps_p50", 0) for v in variants]
    tps_mean = [results[v].get("tps_mean", 0) for v in variants]
    
    # Création du graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = range(len(variants))
    width = 0.35
    
    bars1 = ax.bar([x - width/2 for x in x_pos], tps_p50, width,
                   label='Débit P50', alpha=0.8, color='#2ca02c')
    bars2 = ax.bar([x + width/2 for x in x_pos], tps_mean, width,
                   label='Débit Moyen', alpha=0.8, color='#d62728')
    
    # Personnalisation
    ax.set_xlabel('Variante')
    ax.set_ylabel('Débit (tokens/seconde)')
    ax.set_title('Comparaison des Débits - P50 vs Moyen')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([v.title() for v in variants])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Ajout des valeurs sur les barres
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=9)
    
    autolabel(bars1)
    autolabel(bars2)
    
    plt.tight_layout()
    
    # Sauvegarde
    for ext in ['png', 'svg']:
        output_path = output_file.with_suffix(f'.{ext}')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Graphique sauvegardé: {output_path}")
    
    plt.close()


def create_resource_usage_chart(results: Dict[str, Dict[str, Any]], output_file: Path) -> None:
    """
    Crée un graphique d'utilisation des ressources (mémoire, puissance).
    
    Parameters
    ----------
    results : Dict[str, Dict[str, Any]]
        Résultats de benchmark par variante.
    output_file : Path
        Fichier de sortie pour le graphique.
    """
    if not HAS_MATPLOTLIB:
        return
    
    if not results:
        return
    
    # Préparation des données
    variants = list(results.keys())
    memory_max = [results[v].get("memory_max", 0) for v in variants]
    power_mean = [results[v].get("power_mean", 0) for v in variants]
    
    # Filtrage des valeurs NaN
    memory_max = [m if not (isinstance(m, float) and m != m) else 0 for m in memory_max]
    power_mean = [p if not (isinstance(p, float) and p != p) else 0 for p in power_mean]
    
    # Création du graphique avec deux axes Y
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    x_pos = range(len(variants))
    width = 0.35
    
    # Mémoire (axe gauche)
    color1 = '#9467bd'
    ax1.set_xlabel('Variante')
    ax1.set_ylabel('Mémoire Max (MiB)', color=color1)
    bars1 = ax1.bar([x - width/2 for x in x_pos], memory_max, width,
                    label='Mémoire Max', alpha=0.8, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # Puissance (axe droit)
    ax2 = ax1.twinx()
    color2 = '#ff7f0e'
    ax2.set_ylabel('Puissance Moy (W)', color=color2)
    bars2 = ax2.bar([x + width/2 for x in x_pos], power_mean, width,
                    label='Puissance Moy', alpha=0.8, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Personnalisation
    ax1.set_title('Utilisation des Ressources - Mémoire et Puissance')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([v.title() for v in variants])
    ax1.grid(True, alpha=0.3)
    
    # Légendes combinées
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    
    # Sauvegarde
    for ext in ['png', 'svg']:
        output_path = output_file.with_suffix(f'.{ext}')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Graphique sauvegardé: {output_path}")
    
    plt.close()


def update_docs_results(results: Dict[str, Dict[str, Any]], docs_file: Path) -> None:
    """
    Met à jour le fichier docs/results.md avec les derniers résultats.
    
    Parameters
    ----------
    results : Dict[str, Dict[str, Any]]
        Résultats de benchmark par variante.
    docs_file : Path
        Fichier de documentation à mettre à jour.
    """
    # Création du contenu Markdown
    content = ["# Résultats de Performance", ""]
    content.append(f"*Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    content.append("")
    
    if not results:
        content.append("⚠️ Aucun résultat de benchmark disponible.")
        docs_file.write_text("\n".join(content), encoding="utf-8")
        return
    
    # Graphiques
    content.append("## Graphiques de Performance")
    content.append("")
    content.append("### Latences P50/P95")
    content.append("![Latences](../reports/latency_comparison.png)")
    content.append("")
    content.append("### Débit (Tokens/seconde)")
    content.append("![Débit](../reports/throughput_comparison.png)")
    content.append("")
    content.append("### Utilisation des Ressources")
    content.append("![Ressources](../reports/resource_usage.png)")
    content.append("")
    
    # Tableau de résultats détaillés
    content.append("## Résultats Détaillés")
    content.append("")
    content.append("| Métrique | " + " | ".join(v.title() for v in results.keys()) + " |")
    content.append("|----------|" + "|".join("---" for _ in results) + "|")
    
    metrics = [
        ("Échantillons", "count", "{:.0f}"),
        ("Latence P50 (s)", "latency_p50", "{:.3f}"),
        ("Latence P95 (s)", "latency_p95", "{:.3f}"),
        ("Latence Moy (s)", "latency_mean", "{:.3f}"),
        ("Débit P50 (tok/s)", "tps_p50", "{:.1f}"),
        ("Débit Moy (tok/s)", "tps_mean", "{:.1f}"),
        ("Mémoire Max (MiB)", "memory_max", "{:.0f}"),
        ("Puissance Moy (W)", "power_mean", "{:.1f}"),
    ]
    
    for metric_name, metric_key, fmt in metrics:
        row = [metric_name]
        for variant in results.keys():
            value = results[variant].get(metric_key, float("nan"))
            if isinstance(value, (int, float)) and value == value:  # Pas NaN
                row.append(fmt.format(value))
            else:
                row.append("N/A")
        content.append("| " + " | ".join(row) + " |")
    
    content.append("")
    
    # Accélération si baseline et trtllm présents
    if "baseline" in results and "trtllm" in results:
        baseline_p50 = results["baseline"].get("latency_p50", 0)
        trtllm_p50 = results["trtllm"].get("latency_p50", 0)
        
        if baseline_p50 > 0 and trtllm_p50 > 0:
            speedup = baseline_p50 / trtllm_p50
            content.append("## Accélération")
            content.append("")
            content.append(f"🚀 **TensorRT-LLM** est **{speedup:.2f}x plus rapide** que la baseline HuggingFace.")
            content.append("")
    
    # Instructions de reproduction
    content.append("## Reproduction des Résultats")
    content.append("")
    content.append("Pour reproduire ces résultats :")
    content.append("")
    content.append("```bash")
    content.append("# Lancement du benchmark complet")
    content.append("iol bench --prompts data/prompts.txt --batch-size 1")
    content.append("")
    content.append("# Génération des graphiques")
    content.append("python scripts/export_results.py --reports-dir reports")
    content.append("```")
    content.append("")
    
    # Sauvegarde
    docs_file.parent.mkdir(parents=True, exist_ok=True)
    docs_file.write_text("\n".join(content), encoding="utf-8")
    print(f"📝 Documentation mise à jour: {docs_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère des graphiques et met à jour la documentation"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default="reports",
        help="Répertoire contenant benchmark_results.json"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="reports",
        help="Répertoire de sortie pour les graphiques"
    )
    parser.add_argument(
        "--docs-file",
        type=Path,
        default="docs/results.md",
        help="Fichier de documentation à mettre à jour"
    )
    parser.add_argument(
        "--skip-charts",
        action="store_true",
        help="Ignorer la génération de graphiques"
    )
    parser.add_argument(
        "--skip-docs",
        action="store_true",
        help="Ignorer la mise à jour de la documentation"
    )
    
    args = parser.parse_args()
    
    # Vérification de matplotlib si nécessaire
    if not args.skip_charts and not HAS_MATPLOTLIB:
        print("⚠️  matplotlib non disponible - génération de graphiques désactivée")
        args.skip_charts = True
    
    # Chargement des résultats
    results = load_benchmark_results(args.reports_dir)
    
    if not results:
        print("❌ Aucun résultat de benchmark trouvé", file=sys.stderr)
        sys.exit(1)
    
    print(f"📊 Traitement des résultats pour {len(results)} variantes: {list(results.keys())}")
    
    # Création du répertoire de sortie
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Génération des graphiques
    if not args.skip_charts:
        print("\n📈 Génération des graphiques...")
        
        create_latency_chart(results, args.output_dir / "latency_comparison")
        create_throughput_chart(results, args.output_dir / "throughput_comparison")
        create_resource_usage_chart(results, args.output_dir / "resource_usage")
    
    # Mise à jour de la documentation
    if not args.skip_docs:
        print("\n📝 Mise à jour de la documentation...")
        update_docs_results(results, args.docs_file)
    
    print("\n✅ Export terminé!")


if __name__ == "__main__":
    main()