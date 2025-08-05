"""
inference_optim_llm.engines.baseline
====================================

Implémentation de la variante *baseline* : inférence Hugging Face / PyTorch
sans optimisation TensorRT-LLM.

Fonctionnalités :
-----------------
* Support GPU (FP16 par défaut) & CPU (fallback automatique).
* Gestion du batching (paramètre `batch_size`).
* Mesure pour chaque prompt :
  - latence end-to-end,
  - nombre de tokens générés,
  - mémoire GPU max,
  - puissance moyenne (si NVML disponible).

Exemple
-------
>>> from inference_optim_llm.engines.baseline import HFRunner
>>> runner = HFRunner(model_id="meta-llama/Llama-2-7b-chat-hf", batch_size=2)
>>> runner.generate("Bonjour !")
>>> print(runner.metrics.summary())
"""

from __future__ import annotations

import logging
import math
import os
import time
from pathlib import Path
from typing import List, Sequence

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

from ..core.metrics import MetricsCollector
from ..utils.timing import chrono

try:
    import pynvml  # type: ignore
except ImportError:  # pragma: no cover
    pynvml = None  # type: ignore

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# NVML helpers
# --------------------------------------------------------------------------- #


def _nvml_start() -> tuple[float, float]:
    """Retourne (mémoire_MiB, puissance_W) avant l’exécution."""
    if pynvml is None or not torch.cuda.is_available():
        return math.nan, math.nan
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle).used / 2**20
    pwr = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
    return mem, pwr


def _nvml_stop(t0: float, mem0: float, pwr0: float) -> tuple[float, float]:
    """Retourne (mémoire_max_MiB, puissance_moy_W) sur la période t0→now."""
    if pynvml is None or not torch.cuda.is_available():
        return math.nan, math.nan
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle).used / 2**20
    pwr = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
    pynvml.nvmlShutdown()
    return max(mem0, mem), (pwr0 + pwr) / 2.0 if not math.isnan(pwr0) else pwr


# --------------------------------------------------------------------------- #
# Runner baseline
# --------------------------------------------------------------------------- #


class HFRunner:
    """
    Wrapper léger autour de *transformers* pour la comparaison baseline.

    Paramètres
    ----------
    model_id : str | None
        ID Hugging Face ou chemin local du modèle (défaut : env MODEL_ID).
    batch_size : int
        Nombre de prompts traités simultanément.
    dtype : torch.dtype
        torch.float16 (par défaut), bfloat16, float32…
    device : "cuda" | "cpu"
        Forçage du device (défaut : cuda si dispo, sinon cpu).
    device_map : str | None
        Stratégie de distribution multi-GPU : "auto", "balanced", "balanced_low_0", etc.
        Si None, utilise "auto" pour CUDA ou None pour CPU.
    max_new_tokens : int
        Longueur maximale des réponses générées.

    Attributs
    ---------
    model : transformers.PreTrainedModel
        Modèle HuggingFace chargé.
    tokenizer : transformers.PreTrainedTokenizer
        Tokenizer associé au modèle.
    metrics : MetricsCollector
        Collecteur de métriques pour cette instance.
    gen_cfg : GenerationConfig
        Configuration de génération (max_new_tokens, etc.).

    Exemples
    --------
    >>> # Utilisation simple
    >>> runner = HFRunner("meta-llama/Llama-2-7b-chat-hf")
    >>> response = runner.generate("Bonjour !")
    >>> print(runner.metrics.summary())

    >>> # Multi-GPU avec device_map personnalisé
    >>> runner = HFRunner(
    ...     "meta-llama/Llama-2-13b-chat-hf",
    ...     device_map="balanced_low_0",
    ...     batch_size=4
    ... )
    """

    def __init__(
        self,
        model_id: str | None = None,
        *,
        batch_size: int = 1,
        dtype: torch.dtype | None = None,
        device: str | None = None,
        device_map: str | None = None,
        max_new_tokens: int = 64,
    ) -> None:
        self.model_id = model_id or os.getenv("MODEL_ID", "meta-llama/Llama-2-7b-chat-hf")
        self.batch_size = batch_size
        self.dtype = dtype or torch.float16
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.device_map = device_map
        self.max_new_tokens = max_new_tokens

        # Détermination automatique du device_map si non spécifié
        if self.device_map is None:
            if self.device == "cuda":
                # Utilise "auto" par défaut pour distribuer automatiquement
                self.device_map = "auto"
            else:
                self.device_map = None

        logger.info("Chargement du modèle %s sur %s (device_map=%s)…", 
                   self.model_id, self.device, self.device_map)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        # Gestion du padding token si absent
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=self.dtype,
            device_map=self.device_map,
        )
        
        # Placement explicite sur CPU si demandé
        if self.device == "cpu" and self.device_map is None:
            self.model.to("cpu")
        
        self.model.eval()

        self.gen_cfg = GenerationConfig(max_new_tokens=max_new_tokens)
        self.metrics = MetricsCollector("baseline")

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #

    def generate(self, prompts: str | Sequence[str]) -> List[str]:
        """
        Génère du texte ; renvoie toujours une **liste** de réponses.
        Si `prompts` est une chaîne, elle est transformée en batch d’un élément.
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
        t_start = time.perf_counter()
        mem0, pwr0 = _nvml_start()

        with chrono() as t_total:
            toks = self.tokenizer(
                list(batch), return_tensors="pt", padding=True
            ).to(self.device)
            with torch.no_grad():
                out_ids = self.model.generate(
                    **toks, generation_config=self.gen_cfg
                )

        mem_max, pwr_avg = _nvml_stop(t_start, mem0, pwr0)

        latency_total = t_total()
        latency_per_prompt = latency_total / len(batch)

        decoded = self.tokenizer.batch_decode(out_ids, skip_special_tokens=True)

        len_in = (toks["input_ids"] != self.tokenizer.pad_token_id).sum(dim=1)
        len_out = (out_ids != self.tokenizer.pad_token_id).sum(dim=1)
        new_tokens = (len_out - len_in).tolist()

        for prompt, ntok in zip(batch, new_tokens, strict=True):
            self.metrics.add(
                prompt=prompt,
                latency=latency_per_prompt,
                tokens=int(ntok),
                memory_mb=mem_max,
                power_w=pwr_avg,
            )

        return decoded

    # ------------------------------------------------------------------ #
    # Utilitaire
    # ------------------------------------------------------------------ #

    def save_metrics(self, path: str | Path) -> Path:
        """Sauvegarde les mesures en JSONL et renvoie le chemin créé."""
        return self.metrics.to_json(path)
