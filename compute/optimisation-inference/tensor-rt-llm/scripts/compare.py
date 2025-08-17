#!/usr/bin/env python3
"""
Script de comparaison des résultats de benchmark PyTorch vs TensorRT-LLM
Analyse les fichiers JSON générés et calcule les gains de performance
"""

import json
import os
import sys
import subprocess

# Installation des dépendances si nécessaire
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
except ImportError:
    print("Installation des dépendances pour l'analyse...")
    subprocess.run(['pip', 'install', '--no-cache-dir', 'matplotlib', 'seaborn', 'pandas', 'numpy'], check=True)
    import matplotlib.pyplot as plt
    import seaborn as sns  
    import pandas as pd
    import numpy as np

from datetime import datetime

def load_benchmark_results(pytorch_file, tensorrt_file):
    """Charge les résultats des deux benchmarks"""
    
    if not os.path.exists(pytorch_file):
        print(f"❌ Fichier PyTorch non trouvé: {pytorch_file}")
        return None, None
        
    if not os.path.exists(tensorrt_file):
        print(f"❌ Fichier TensorRT non trouvé: {tensorrt_file}")
        return None, None
    
    try:
        with open(pytorch_file, 'r') as f:
            pytorch_results = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {pytorch_file}: {e}")
        return None, None
        
    try:
        with open(tensorrt_file, 'r') as f:
            tensorrt_results = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {tensorrt_file}: {e}")
        return pytorch_results, None
    
    return pytorch_results, tensorrt_results

def calculate_speedup(pytorch_results, tensorrt_results):
    """Calcule les gains de performance"""
    
    if not pytorch_results or not tensorrt_results:
        return None
    
    pytorch_summary = pytorch_results.get('summary', {})
    tensorrt_summary = tensorrt_results.get('summary', {})
    
    # Éviter la division par zéro
    pytorch_latency = pytorch_summary.get('avg_latency_ms', 1)
    pytorch_throughput = pytorch_summary.get('avg_throughput_tokens_per_sec', 1)
    pytorch_memory = pytorch_summary.get('avg_memory_usage_gb', 0)
    
    tensorrt_latency = tensorrt_summary.get('avg_latency_ms', 1)
    tensorrt_throughput = tensorrt_summary.get('avg_throughput_tokens_per_sec', 1)
    tensorrt_memory = tensorrt_summary.get('avg_memory_usage_gb', 0)
    
    speedup_data = {
        "latency_improvement": {
            "pytorch_ms": pytorch_latency,
            "tensorrt_ms": tensorrt_latency,
            "speedup_factor": pytorch_latency / tensorrt_latency if tensorrt_latency > 0 else 0,
            "improvement_percent": ((pytorch_latency - tensorrt_latency) / pytorch_latency * 100) if pytorch_latency > 0 else 0
        },
        "throughput_improvement": {
            "pytorch_tokens_per_sec": pytorch_throughput,
            "tensorrt_tokens_per_sec": tensorrt_throughput,
            "speedup_factor": tensorrt_throughput / pytorch_throughput if pytorch_throughput > 0 else 0,
            "improvement_percent": ((tensorrt_throughput - pytorch_throughput) / pytorch_throughput * 100) if pytorch_throughput > 0 else 0
        },
        "memory_comparison": {
            "pytorch_gb": pytorch_memory,
            "tensorrt_gb": tensorrt_memory,
            "memory_ratio": tensorrt_memory / pytorch_memory if pytorch_memory > 0 else 0,
            "memory_change_percent": ((tensorrt_memory - pytorch_memory) / pytorch_memory * 100) if pytorch_memory > 0 else 0
        }
    }
    
    return speedup_data

def create_comparison_plots(pytorch_results, tensorrt_results, output_dir="data/results"):
    """Crée des graphiques de comparaison"""
    
    if not pytorch_results or not tensorrt_results:
        print("⚠️  Impossible de créer les graphiques sans les deux jeux de résultats")
        return
    
    # Style des graphiques
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Comparaison PyTorch vs TensorRT-LLM', fontsize=16, fontweight='bold')
    
    # Données pour les graphiques
    pytorch_metrics = pytorch_results.get('metrics', {})
    tensorrt_metrics = tensorrt_results.get('metrics', {})
    
    # 1. Comparaison de latence
    ax1 = axes[0, 0]
    latency_data = [
        pytorch_metrics.get('latency_ms', []),
        tensorrt_metrics.get('latency_ms', [])
    ]
    labels = ['PyTorch', 'TensorRT-LLM']
    colors = ['#ff6b6b', '#4ecdc4']
    
    bp1 = ax1.boxplot(latency_data, labels=labels, patch_artist=True)
    for patch, color in zip(bp1['boxes'], colors):
        patch.set_facecolor(color)
    ax1.set_title('Latence (ms)')
    ax1.set_ylabel('Milliseconds')
    ax1.grid(True, alpha=0.3)
    
    # 2. Comparaison de débit
    ax2 = axes[0, 1]
    throughput_data = [
        pytorch_metrics.get('throughput_tokens_per_sec', []),
        tensorrt_metrics.get('throughput_tokens_per_sec', [])
    ]
    
    bp2 = ax2.boxplot(throughput_data, labels=labels, patch_artist=True)
    for patch, color in zip(bp2['boxes'], colors):
        patch.set_facecolor(color)
    ax2.set_title('Débit (tokens/sec)')
    ax2.set_ylabel('Tokens par seconde')
    ax2.grid(True, alpha=0.3)
    
    # 3. Évolution de la latence au fil des itérations
    ax3 = axes[1, 0]
    pytorch_latencies = pytorch_metrics.get('latency_ms', [])
    tensorrt_latencies = tensorrt_metrics.get('latency_ms', [])
    
    if pytorch_latencies and tensorrt_latencies:
        iterations = range(1, min(len(pytorch_latencies), len(tensorrt_latencies)) + 1)
        ax3.plot(iterations, pytorch_latencies[:len(iterations)], 'o-', color='#ff6b6b', label='PyTorch', linewidth=2)
        ax3.plot(iterations, tensorrt_latencies[:len(iterations)], 's-', color='#4ecdc4', label='TensorRT-LLM', linewidth=2)
        ax3.set_title('Évolution de la latence')
        ax3.set_xlabel('Itération')
        ax3.set_ylabel('Latence (ms)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # 4. Barres de comparaison des moyennes
    ax4 = axes[1, 1]
    pytorch_summary = pytorch_results.get('summary', {})
    tensorrt_summary = tensorrt_results.get('summary', {})
    
    metrics_names = ['Latence (ms)', 'Débit (tok/s)', 'Mémoire (GB)']
    pytorch_values = [
        pytorch_summary.get('avg_latency_ms', 0),
        pytorch_summary.get('avg_throughput_tokens_per_sec', 0),
        pytorch_summary.get('avg_memory_usage_gb', 0)
    ]
    tensorrt_values = [
        tensorrt_summary.get('avg_latency_ms', 0),
        tensorrt_summary.get('avg_throughput_tokens_per_sec', 0),
        tensorrt_summary.get('avg_memory_usage_gb', 0)
    ]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, pytorch_values, width, label='PyTorch', color='#ff6b6b', alpha=0.8)
    bars2 = ax4.bar(x + width/2, tensorrt_values, width, label='TensorRT-LLM', color='#4ecdc4', alpha=0.8)
    
    ax4.set_title('Comparaison des moyennes')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics_names)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Ajout des valeurs sur les barres
    for bar in bars1:
        height = bar.get_height()
        ax4.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax4.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    # Sauvegarde du graphique
    plot_file = os.path.join(output_dir, 'benchmark_comparison.png')
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"📊 Graphiques sauvegardés dans: {plot_file}")
    
    return plot_file

def print_detailed_comparison(speedup_data):
    """Affiche un rapport détaillé de comparaison"""
    
    if not speedup_data:
        print("❌ Pas de données de comparaison disponibles")
        return
    
    print("\n" + "="*60)
    print("🚀 RAPPORT DE PERFORMANCE - TensorRT-LLM vs PyTorch")
    print("="*60)
    
    # Latence
    latency = speedup_data['latency_improvement']
    print(f"\n📈 LATENCE:")
    print(f"   PyTorch:     {latency['pytorch_ms']:.1f} ms")
    print(f"   TensorRT:    {latency['tensorrt_ms']:.1f} ms")
    print(f"   📊 Speedup:   {latency['speedup_factor']:.2f}x")
    print(f"   📉 Réduction: {latency['improvement_percent']:.1f}%")
    
    # Débit
    throughput = speedup_data['throughput_improvement']
    print(f"\n⚡ DÉBIT:")
    print(f"   PyTorch:     {throughput['pytorch_tokens_per_sec']:.1f} tokens/s")
    print(f"   TensorRT:    {throughput['tensorrt_tokens_per_sec']:.1f} tokens/s")
    print(f"   📊 Speedup:   {throughput['speedup_factor']:.2f}x")
    print(f"   📈 Gain:      {throughput['improvement_percent']:.1f}%")
    
    # Mémoire
    memory = speedup_data['memory_comparison']
    print(f"\n💾 MÉMOIRE GPU:")
    print(f"   PyTorch:     {memory['pytorch_gb']:.2f} GB")
    print(f"   TensorRT:    {memory['tensorrt_gb']:.2f} GB")
    print(f"   📊 Ratio:     {memory['memory_ratio']:.2f}x")
    print(f"   📉 Variation: {memory['memory_change_percent']:+.1f}%")
    
    # Résumé
    print(f"\n🎯 RÉSUMÉ:")
    if latency['speedup_factor'] > 1:
        print(f"   ✅ TensorRT-LLM est {latency['speedup_factor']:.1f}x plus rapide en latence")
    else:
        print(f"   ⚠️  PyTorch est plus rapide en latence")
        
    if throughput['speedup_factor'] > 1:
        print(f"   ✅ TensorRT-LLM a un débit {throughput['speedup_factor']:.1f}x supérieur")
    else:
        print(f"   ⚠️  PyTorch a un meilleur débit")
        
    if memory['memory_change_percent'] < 0:
        print(f"   ✅ TensorRT-LLM utilise {abs(memory['memory_change_percent']):.1f}% moins de mémoire")
    else:
        print(f"   ⚠️  TensorRT-LLM utilise {memory['memory_change_percent']:.1f}% plus de mémoire")

def save_comparison_report(pytorch_results, tensorrt_results, speedup_data, output_dir="data/results"):
    """Sauvegarde un rapport de comparaison complet"""
    
    report = {
        "comparison_timestamp": datetime.now().isoformat(),
        "model": "TinyLlama-1.1B-Chat",
        "pytorch_results": pytorch_results,
        "tensorrt_results": tensorrt_results,
        "speedup_analysis": speedup_data,
        "conclusion": {
            "latency_winner": "tensorrt" if speedup_data and speedup_data['latency_improvement']['speedup_factor'] > 1 else "pytorch",
            "throughput_winner": "tensorrt" if speedup_data and speedup_data['throughput_improvement']['speedup_factor'] > 1 else "pytorch",
            "memory_efficiency": "tensorrt" if speedup_data and speedup_data['memory_comparison']['memory_change_percent'] < 0 else "pytorch"
        }
    }
    
    report_file = os.path.join(output_dir, 'benchmark_comparison_report.json')
    
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📋 Rapport complet sauvegardé dans: {report_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du rapport: {e}")

def main():
    """Fonction principale"""
    
    # Chemins par défaut
    results_dir = "data/results"
    pytorch_file = os.path.join(results_dir, "pytorch_benchmark.json")
    tensorrt_file = os.path.join(results_dir, "tensorrt_benchmark.json")
    
    # Arguments en ligne de commande
    if len(sys.argv) > 1:
        pytorch_file = sys.argv[1]
    if len(sys.argv) > 2:
        tensorrt_file = sys.argv[2]
    
    print("🔍 Analyse des résultats de benchmark...")
    print(f"📁 PyTorch:    {pytorch_file}")
    print(f"📁 TensorRT:   {tensorrt_file}")
    
    # Chargement des résultats
    pytorch_results, tensorrt_results = load_benchmark_results(pytorch_file, tensorrt_file)
    
    if not pytorch_results and not tensorrt_results:
        print("❌ Aucun résultat de benchmark trouvé!")
        sys.exit(1)
    
    # Calcul des gains de performance
    speedup_data = calculate_speedup(pytorch_results, tensorrt_results)
    
    # Affichage du rapport
    print_detailed_comparison(speedup_data)
    
    # Création des graphiques
    if pytorch_results and tensorrt_results:
        create_comparison_plots(pytorch_results, tensorrt_results, results_dir)
    
    # Sauvegarde du rapport complet
    save_comparison_report(pytorch_results, tensorrt_results, speedup_data, results_dir)
    
    print(f"\n✅ Analyse terminée! Fichiers générés dans {results_dir}")

if __name__ == "__main__":
    main()
