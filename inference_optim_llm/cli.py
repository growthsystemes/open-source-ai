"""
Interface CLI pour inference_optim_llm.

Commandes disponibles :
- download : Télécharge un modèle HuggingFace
- build : Compile un engine TensorRT-LLM
- run : Lance l'inférence avec une variante (baseline ou trtllm)
- bench : Lance un benchmark complet (baseline + trtllm)
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import List, Optional

import typer

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAS_RICH = True
except ImportError:
    # Fallback si rich n'est pas disponible
    HAS_RICH = False
    Console = None  # type: ignore
    Progress = None  # type: ignore
    SpinnerColumn = None  # type: ignore
    TextColumn = None  # type: ignore

from .build.builder import convert_and_build, TensorRTEngineBuilder
from .core.metrics import MetricsCollector
# Imports conditionnels pour éviter les erreurs d'environnement
from .engines.baseline import HFRunner

# Import TensorRT-LLM seulement si disponible
try:
    from .engines.trt import TRTRunner
    HAS_TENSORRT = True
except ImportError:
    TRTRunner = None
    HAS_TENSORRT = False

# Configuration
app = typer.Typer(help="🚀 Interface CLI pour optimisation d'inférence LLM")

# Console avec fallback
if HAS_RICH:
    console = Console()
else:
    # Console simple sans rich
    class SimpleConsole:
        def print(self, text: str, style: str = "") -> None:
            print(text)
    console = SimpleConsole()  # type: ignore

logger = logging.getLogger(__name__)


@app.command()
def download(
    model_id: str,
    local_dir: Optional[Path] = None,
    resume: bool = True,
) -> None:
    """
    Télécharge un modèle depuis HuggingFace Hub.
    
    Args:
        model_id: ID du modèle (ex: meta-llama/Llama-2-7b-chat-hf)
        local_dir: Répertoire de destination (défaut: ~/.cache/hfmodels)
        resume: Reprendre un téléchargement interrompu
    """
    if local_dir is None:
        local_dir = Path.home() / ".cache" / "hfmodels"
    
    console.print(f"📥 Téléchargement de {model_id} vers {local_dir}")
    
    cmd = [
        "huggingface-cli", "download", model_id,
        "--local-dir", str(local_dir),
    ]
    
    if resume:
        cmd.append("--resume-download")
    
    try:
        subprocess.run(cmd, check=True)
        console.print("✅ Téléchargement terminé", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Erreur de téléchargement: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def build(
    model_id: str,
    precision: str = "fp16",
    quant_mode: Optional[str] = None,
    calibration_path: Optional[Path] = None,
    batch_size: int = 1,
    max_input_len: int = 4096,
    max_output_len: int = 2048,
) -> None:
    """
    Compile un engine TensorRT-LLM.
    
    Args:
        model_id: ID du modèle HuggingFace
        precision: Précision (fp16, fp32, int8)
        quant_mode: Mode de quantification pour INT8
        calibration_path: Chemin vers données de calibration
        batch_size: Taille de batch maximum
        max_input_len: Longueur max d'entrée
        max_output_len: Longueur max de sortie
    """
    console.print(f"🔧 Compilation engine TensorRT-LLM pour {model_id}")
    
    builder = TensorRTEngineBuilder(
        model_id=model_id,
        precision=precision,
        quant_mode=quant_mode,
        calibration_path=str(calibration_path) if calibration_path else None,
        batch_size=batch_size,
        max_input_len=max_input_len,
        max_output_len=max_output_len,
    )
    
    try:
        if HAS_RICH and Progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Compilation en cours...", total=None)
                engine_path = builder.build()
                progress.stop()
        else:
            console.print("Compilation en cours...")
            engine_path = builder.build()
        
        console.print(f"✅ Engine prêt: {engine_path}", style="green")
        
        # Affichage des informations de l'engine
        info = builder.get_engine_info()
        console.print("\n📊 Configuration de l'engine:")
        for key, value in info.items():
            console.print(f"  {key}: {value}")
            
    except Exception as e:
        console.print(f"❌ Erreur de compilation: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def run(
    variant: str = typer.Argument(..., help="Variante: 'baseline' ou 'trtllm'"),
    prompts_file: Path = typer.Option(Path("data/prompts.txt"), help="Fichier de prompts"),
    batch_size: int = typer.Option(1, help="Taille de batch"),
    max_new_tokens: int = typer.Option(64, help="Tokens max à générer"),
    save_json: Optional[Path] = typer.Option(None, help="Sauvegarder en JSONL"),
    quiet: bool = typer.Option(False, help="Mode silencieux"),
) -> None:
    """
    Lance l'inférence avec une variante spécifique.
    
    Args:
        variant: Type de runner ('baseline' ou 'trtllm')
        prompts_file: Fichier contenant les prompts (un par ligne)
        batch_size: Taille de batch pour le traitement
        max_new_tokens: Nombre max de tokens à générer
        save_json: Chemin pour sauvegarder les métriques en JSONL
        quiet: Supprime l'affichage du résumé JSON
    """
    # Vérification des variants disponibles
    available_variants = ["baseline", "trtllm"]  # Toujours permettre trtllm
    
    if variant not in available_variants:
        console.print(f"❌ Variante inconnue: {variant}", style="red")
        console.print(f"💡 Variants disponibles: {', '.join(available_variants)}", style="yellow")
        raise typer.Exit(1)
    
    # Vérification spécifique pour TensorRT-LLM
    if variant == "trtllm" and not HAS_TENSORRT:
        console.print("⚠️ TensorRT-LLM non disponible dans cet environnement", style="yellow")
        console.print("💡 Le container va continuer avec le fallback baseline GPU", style="yellow")
    
    if not prompts_file.exists():
        console.print(f"❌ Fichier de prompts introuvable: {prompts_file}", style="red")
        raise typer.Exit(1)
    
    # Chargement des prompts
    prompts = prompts_file.read_text(encoding="utf-8").strip().splitlines()
    if not prompts:
        console.print("❌ Aucun prompt trouvé dans le fichier", style="red")
        raise typer.Exit(1)
    
    console.print(f"🚀 Lancement {variant} avec {len(prompts)} prompts")
    
    # Reset des métriques pour éviter les interférences
    MetricsCollector.reset_all()
    
    # Initialisation du runner
    try:
        if variant == "baseline":
            runner = HFRunner(
                batch_size=batch_size,
                max_new_tokens=max_new_tokens,
            )
        else:  # trtllm
            if not HAS_TENSORRT:
                console.print("⚠️ TensorRT-LLM non disponible - utilisation du fallback baseline GPU", style="yellow")
                runner = HFRunner(
                    batch_size=batch_size,
                    max_new_tokens=max_new_tokens,
                )
            else:
                runner = TRTRunner(
                    batch_size=batch_size,
                    max_new_tokens=max_new_tokens,
                )
    except Exception as e:
        console.print(f"❌ Erreur d'initialisation {variant}: {e}", style="red")
        raise typer.Exit(1)
    
    # Exécution avec barre de progression
    try:
        if HAS_RICH and Progress:
            with Progress(console=console) as progress:
                task = progress.add_task(f"Traitement {variant}...", total=len(prompts))
                
                for prompt in prompts:
                    runner.generate(prompt)
                    progress.advance(task)
        else:
            console.print(f"Traitement {variant} de {len(prompts)} prompts...")
            for i, prompt in enumerate(prompts, 1):
                runner.generate(prompt)
                if i % 10 == 0:  # Affichage périodique
                    console.print(f"  Traité {i}/{len(prompts)} prompts")
        
        console.print("✅ Traitement terminé", style="green")
        
        # Sauvegarde JSONL si demandée
        if save_json:
            output_path = runner.save_metrics(save_json)
            console.print(f"💾 Métriques sauvegardées: {output_path}")
        
        # Affichage du résumé (sauf en mode quiet)
        if not quiet:
            summary = MetricsCollector.dump_all()
            console.print("\n📊 Résumé des métriques:")
            console.print(json.dumps(summary, indent=2, ensure_ascii=False))
            
    except Exception as e:
        console.print(f"❌ Erreur durant l'exécution: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def bench(
    prompts_file: Path = typer.Option(Path("data/prompts.txt"), help="Fichier de prompts"),
    batch_size: int = typer.Option(1, help="Taille de batch"),
    max_new_tokens: int = typer.Option(64, help="Tokens max à générer"),
    precision: str = typer.Option("fp16", help="Précision pour TensorRT-LLM"),
    output_dir: Path = typer.Option(Path("reports"), help="Répertoire de sortie"),
    skip_baseline: bool = typer.Option(False, help="Ignorer baseline"),
    skip_trtllm: bool = typer.Option(False, help="Ignorer TensorRT-LLM"),
) -> None:
    """
    Lance un benchmark complet (baseline + TensorRT-LLM).
    
    Args:
        prompts_file: Fichier de prompts pour le benchmark
        batch_size: Taille de batch pour les deux variantes
        max_new_tokens: Tokens max à générer
        precision: Précision TensorRT-LLM (fp16, int8, etc.)
        output_dir: Répertoire pour les rapports
        skip_baseline: Ignorer l'exécution baseline
        skip_trtllm: Ignorer l'exécution TensorRT-LLM
    """
    if skip_baseline and skip_trtllm:
        console.print("❌ Impossible d'ignorer les deux variantes", style="red")
        raise typer.Exit(1)
    
    # Préparation du répertoire de sortie
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"🏁 Début du benchmark avec {prompts_file}")
    start_time = time.time()
    
    results = {}
    
    # Exécution baseline
    if not skip_baseline:
        console.print("\n" + "="*50)
        console.print("📊 Phase 1: Baseline (HuggingFace)", style="bold blue")
        console.print("="*50)
        
        try:
            # Reset des métriques
            MetricsCollector.reset_all()
            
            # Exécution
            runner = HFRunner(
                batch_size=batch_size,
                max_new_tokens=max_new_tokens,
            )
            
            prompts = prompts_file.read_text(encoding="utf-8").strip().splitlines()
            
            if HAS_RICH and Progress:
                with Progress(console=console) as progress:
                    task = progress.add_task("Baseline...", total=len(prompts))
                    for prompt in prompts:
                        runner.generate(prompt)
                        progress.advance(task)
            else:
                console.print(f"Traitement baseline de {len(prompts)} prompts...")
                for i, prompt in enumerate(prompts, 1):
                    runner.generate(prompt)
                    if i % 10 == 0:
                        console.print(f"  Baseline: {i}/{len(prompts)} prompts")
            
            # Sauvegarde des résultats
            baseline_file = output_dir / "baseline.jsonl"
            runner.save_metrics(baseline_file)
            results["baseline"] = runner.metrics.summary()
            
            console.print(f"✅ Baseline terminée - résultats: {baseline_file}", style="green")
            
        except Exception as e:
            console.print(f"❌ Erreur baseline: {e}", style="red")
            if not skip_trtllm:
                console.print("Continuation avec TensorRT-LLM...")
            else:
                raise typer.Exit(1)
    
    # Exécution TensorRT-LLM
    if not skip_trtllm:
        console.print("\n" + "="*50)
        console.print("🚄 Phase 2: TensorRT-LLM", style="bold green")
        console.print("="*50)
        
        try:
            # Reset des métriques
            MetricsCollector.reset_all()
            
            # Exécution
            runner = TRTRunner(
                batch_size=batch_size,
                max_new_tokens=max_new_tokens,
                precision=precision,
            )
            
            prompts = prompts_file.read_text(encoding="utf-8").strip().splitlines()
            
            if HAS_RICH and Progress:
                with Progress(console=console) as progress:
                    task = progress.add_task("TensorRT-LLM...", total=len(prompts))
                    for prompt in prompts:
                        runner.generate(prompt)
                        progress.advance(task)
            else:
                console.print(f"Traitement TensorRT-LLM de {len(prompts)} prompts...")
                for i, prompt in enumerate(prompts, 1):
                    runner.generate(prompt)
                    if i % 10 == 0:
                        console.print(f"  TensorRT-LLM: {i}/{len(prompts)} prompts")
            
            # Sauvegarde des résultats
            trtllm_file = output_dir / "trtllm.jsonl"
            runner.save_metrics(trtllm_file)
            results["trtllm"] = runner.metrics.summary()
            
            console.print(f"✅ TensorRT-LLM terminé - résultats: {trtllm_file}", style="green")
            
        except Exception as e:
            console.print(f"❌ Erreur TensorRT-LLM: {e}", style="red")
            if not results:  # Aucun résultat disponible
                raise typer.Exit(1)
    
    # Génération du rapport de comparaison
    total_time = time.time() - start_time
    
    console.print("\n" + "="*50)
    console.print("📊 RÉSULTATS DU BENCHMARK", style="bold magenta")
    console.print("="*50)
    
    if results:
        # Sauvegarde du rapport combiné
        report_file = output_dir / "benchmark_results.json"
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": total_time,
            "config": {
                "prompts_file": str(prompts_file),
                "batch_size": batch_size,
                "max_new_tokens": max_new_tokens,
                "precision": precision,
            },
            "results": results,
        }
        
        report_file.write_text(json.dumps(report_data, indent=2, ensure_ascii=False))
        console.print(f"📄 Rapport sauvegardé: {report_file}")
        
        # Affichage de la comparaison
        console.print("\n🔍 Comparaison des performances:")
        
        for variant, summary in results.items():
            console.print(f"\n{variant.upper()}:")
            console.print(f"  Échantillons: {summary['count']}")
            console.print(f"  Latence P50: {summary.get('latency_p50', 'N/A'):.3f}s")
            console.print(f"  Latence P95: {summary.get('latency_p95', 'N/A'):.3f}s")
            console.print(f"  Débit P50: {summary.get('tps_p50', 'N/A'):.1f} tok/s")
            
            if "memory_max" in summary:
                console.print(f"  Mémoire max: {summary['memory_max']:.0f} MiB")
            if "power_mean" in summary:
                console.print(f"  Puissance moy: {summary['power_mean']:.1f} W")
        
        # Calcul de l'accélération si les deux variantes sont présentes
        if "baseline" in results and "trtllm" in results:
            baseline_p50 = results["baseline"].get("latency_p50", 0)
            trtllm_p50 = results["trtllm"].get("latency_p50", 0)
            
            if baseline_p50 > 0 and trtllm_p50 > 0:
                speedup = baseline_p50 / trtllm_p50
                console.print(f"\n🚀 Accélération TensorRT-LLM: {speedup:.1f}x", style="bold green")
    
    console.print(f"\n⏱️  Temps total: {total_time:.1f}s")
    console.print("✅ Benchmark terminé!", style="bold green")


if __name__ == "__main__":
    app()
