"""
inference_optim_llm.engines.trt
===============================

Implémentation TensorRT-LLM optimisée pour l'inférence GPU haute performance.

Fonctionnalités :
-----------------
* Support des engines TensorRT-LLM pré-compilés.
* Mesure de métriques complètes (latence, mémoire, puissance via NVML).
* Gestion configurable du batch_size et max_new_tokens.
* Exposition des phases prefill/decode si disponibles dans les timings.
"""

from __future__ import annotations

import logging
import math
import os
import time
from pathlib import Path
from typing import List, Sequence

from tensorrt_llm.runtime import LLM, ModelConfig, GenerationConfig

from ..core.metrics import MetricsCollector
from ..utils.timing import chrono

try:
    import pynvml  # type: ignore
except ImportError:  # pragma: no cover
    pynvml = None  # type: ignore

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# NVML helpers (réutilisation du code baseline)
# --------------------------------------------------------------------------- #


def _nvml_start() -> tuple[float, float]:
    """Retourne (mémoire_MiB, puissance_W) avant l'exécution."""
    if pynvml is None:
        return math.nan, math.nan
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle).used / 2**20
        pwr = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
        return mem, pwr
    except Exception:  # pragma: no cover
        return math.nan, math.nan


def _nvml_stop(t0: float, mem0: float, pwr0: float) -> tuple[float, float]:
    """Retourne (mémoire_max_MiB, puissance_moy_W) sur la période t0→now."""
    if pynvml is None:
        return math.nan, math.nan
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle).used / 2**20
        pwr = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
        pynvml.nvmlShutdown()
        return max(mem0, mem), (pwr0 + pwr) / 2.0 if not math.isnan(pwr0) else pwr
    except Exception:  # pragma: no cover
        return math.nan, math.nan


# --------------------------------------------------------------------------- #
# Runner TensorRT-LLM
# --------------------------------------------------------------------------- #


class TRTRunner:
    """
    Wrapper pour TensorRT-LLM avec parité fonctionnelle avec HFRunner.

    Paramètres
    ----------
    model_id : str | None
        ID du modèle (utilisé pour construire le chemin de l'engine).
    engine_path : str | None
        Chemin explicite vers l'engine TensorRT-LLM.
    precision : str
        Précision utilisée (fp16, int8, etc.).
    batch_size : int
        Taille de batch pour le traitement groupé.
    max_new_tokens : int
        Nombre maximum de tokens à générer.
    tokenizer_path : str
        Chemin vers le tokenizer (défaut : /workspace/models/).
    """

    def __init__(
        self,
        model_id: str | None = None,
        *,
        engine_path: str | None = None,
        precision: str | None = None,
        batch_size: int = 1,
        max_new_tokens: int = 64,
        tokenizer_path: str = "/workspace/models/",
    ) -> None:
        self.model_id = model_id or os.getenv("MODEL_ID", "meta-llama/Llama-2-7b-chat-hf")
        self.precision = precision or os.getenv("TRT_PRECISION", "fp16")
        self.batch_size = batch_size
        self.max_new_tokens = max_new_tokens

        # Construction du chemin de l'engine
        if engine_path is None:
            engine_name = f"{self.model_id.split('/')[-1]}.{self.precision}.engine"
            self.engine_path = f"/workspace/engines/{engine_name}"
        else:
            self.engine_path = engine_path

        logger.info("Chargement de l'engine TensorRT-LLM : %s", self.engine_path)
        
        # Vérification de l'existence de l'engine
        if not Path(self.engine_path).exists():
            raise FileNotFoundError(f"Engine TensorRT-LLM introuvable : {self.engine_path}")

        # Initialisation du modèle
        model_config = ModelConfig(tokenizer_path=tokenizer_path)
        self.llm = LLM(self.engine_path, model_config)
        
        # Configuration de génération
        self.gen_cfg = GenerationConfig(max_new_tokens=max_new_tokens)
        
        # Collecteur de métriques
        self.metrics = MetricsCollector("trtllm")

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #

    def generate(self, prompts: str | Sequence[str]) -> List[str]:
        """
        Génère du texte avec TensorRT-LLM.
        
        Paramètres
        ----------
        prompts : str | Sequence[str]
            Prompt(s) à traiter.
            
        Returns
        -------
        List[str]
            Réponses générées (toujours une liste).
        """
        prompts_list = [prompts] if isinstance(prompts, str) else list(prompts)
        outputs: List[str] = []

        for i in range(0, len(prompts_list), self.batch_size):
            batch = prompts_list[i : i + self.batch_size]
            outputs.extend(self._generate_batch(batch))

        return outputs

    # ------------------------------------------------------------------ #
    # Implémentation interne
    # ------------------------------------------------------------------ #

    def _generate_batch(self, batch: Sequence[str]) -> List[str]:
        """Traite un batch de prompts avec mesures de performances."""
        t_start = time.perf_counter()
        mem0, pwr0 = _nvml_start()

        outputs = []
        
        for prompt in batch:
            with chrono() as t_total:
                rsp = self.llm.generate(prompt, self.gen_cfg)
            
            # Extraction des métriques
            latency_total = t_total()
            tokens_generated = getattr(rsp, 'generated_tokens', len(rsp.text.split()))
            
            # Gestion des timings détaillés (prefill/decode) si disponibles
            prefill_latency = math.nan
            decode_latency = math.nan
            
            if hasattr(rsp, 'timings') and rsp.timings:
                try:
                    timings = rsp.timings
                    if hasattr(timings, 'prefill_time'):
                        prefill_latency = timings.prefill_time
                    if hasattr(timings, 'decode_time'):
                        decode_latency = timings.decode_time
                except Exception:  # pragma: no cover
                    pass  # Continue avec NaN si extraction échoue
            
            outputs.append(rsp.text)

        # Mesures NVML finales
        mem_max, pwr_avg = _nvml_stop(t_start, mem0, pwr0)
        
        # Enregistrement des métriques (moyenne par prompt dans le batch)
        latency_per_prompt = latency_total / len(batch) if batch else 0.0
        
        for i, prompt in enumerate(batch):
            # Pour l'instant, on utilise la latence moyenne
            # TODO: Améliorer pour avoir la latence individuelle par prompt
            tokens = tokens_generated if i == 0 else 0  # Simplification temporaire
            
            self.metrics.add(
                prompt=prompt,
                latency=latency_per_prompt,
                tokens=tokens,
                memory_mb=mem_max,
                power_w=pwr_avg,
            )
            
            # Si on a les timings détaillés, on peut les enregistrer séparément
            # TODO: Étendre MetricsCollector pour supporter prefill/decode
            if not math.isnan(prefill_latency):
                logger.debug("Prefill latency: %.3fs, Decode latency: %.3fs", 
                           prefill_latency, decode_latency)

        return outputs

    # ------------------------------------------------------------------ #
    # Utilitaire
    # ------------------------------------------------------------------ #

    def save_metrics(self, path: str | Path) -> Path:
        """Sauvegarde les mesures en JSONL et renvoie le chemin créé."""
        return self.metrics.to_json(path)
