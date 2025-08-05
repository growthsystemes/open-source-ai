"""
inference_optim_llm.core.metrics
================================

Collecte **uniforme** des métriques d’inférence pour toutes les variantes
(baseline, TensorRT-LLM, TGI, etc.).

Principales fonctionnalités
---------------------------
* `MetricsCollector` – 1 instance par variante (singleton par *name*).
* Stocke pour chaque prompt :
  - latence end-to-end *(s)*,
  - nb de tokens générés,
  - mémoire GPU max *(MiB)*,
  - puissance moyenne *(W)*.
* Méthodes de synthèse : p50 / p95, moyenne, max.
* Export :
  - `to_json(path)`  → fichier JSONL (1 ligne = 1 sample),
  - `summary()`      → `dict` prêt à sérialiser,
  - `dump_all()`     → agrège toutes les instances ;
    renvoie un objet `{variant: summary}`.
"""

from __future__ import annotations

import contextlib
import json
import math
import statistics as stats
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    # Lazy-import : disponible dans les conteneurs GPU, absent en CPU.
    import pynvml  # type: ignore
except ImportError:  # pragma: no cover – tests CPU only
    pynvml = None  # type: ignore

try:
    import numpy as np  # type: ignore
    HAS_NUMPY = True
except ImportError:  # pragma: no cover
    np = None  # type: ignore
    HAS_NUMPY = False


# --------------------------------------------------------------------------- #
# Utilitaires internes
# --------------------------------------------------------------------------- #


def _percentile(values: List[float], pct: float) -> float:
    """
    Calcul optimisé de percentile avec fallback numpy → implémentation pure Python.
    
    Paramètres
    ----------
    values : List[float]
        Liste de valeurs numériques.
    pct : float
        Percentile à calculer (0-100).
        
    Returns
    -------
    float
        Valeur du percentile demandé, ou NaN si liste vide.
    """
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]

    # Utilise numpy si disponible (plus rapide et plus précis)
    if HAS_NUMPY and np is not None:
        try:
            return float(np.percentile(values, pct))
        except Exception:  # pragma: no cover
            pass  # Fallback vers implémentation pure Python

    # Implémentation pure Python (fallback)
    values_sorted = sorted(values)
    k = (len(values_sorted) - 1) * pct / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values_sorted[int(k)]
    d0 = values_sorted[int(f)] * (c - k)
    d1 = values_sorted[int(c)] * (k - f)
    return d0 + d1


@contextlib.contextmanager
def _nvml_sample() -> "SparseGpuSample":
    """
    Context-manager qui lit la mémoire/power GPU avant et après un bloc
    et calcule un delta/average. Si NVML absent → valeurs NaN.
    """
    if pynvml is None:
        yield SparseGpuSample(math.nan, math.nan)
        return

    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    mem0 = pynvml.nvmlDeviceGetMemoryInfo(handle).used / (1024 ** 2)
    pow0 = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
    t0 = time.perf_counter()

    yield SparseGpuSample(math.nan, math.nan)  # Utilisation externe inutile.

    mem1 = pynvml.nvmlDeviceGetMemoryInfo(handle).used / (1024 ** 2)
    pow1 = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
    dt = max(time.perf_counter() - t0, 1e-9)
    pynvml.nvmlShutdown()

    # mettre à jour les champs de sortie
    sample = SparseGpuSample(max(mem0, mem1), (pow0 + pow1) / 2.0)
    yield sample  # pragma: no cover  – appelé implicitement


@dataclass(slots=True)
class SparseGpuSample:
    """Mesure mémoire / puissance (peut contenir des NaN si non dispo)."""

    memory_mb: float
    power_w: float


@dataclass(slots=True)
class _Sample:
    """1 ligne brute (non agrégée) de métriques."""

    prompt: str
    latency: float          # secondes
    tokens: int
    memory_mb: float        # MiB
    power_w: float          # Watts

    # --------------------------------------------------------------------- #
    # Conversion helpers
    # --------------------------------------------------------------------- #

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Ajout d'un débit (tokens/s) direct pour ergonomie
        d["tps"] = self.tokens / self.latency if self.latency else float("nan")
        return d


# --------------------------------------------------------------------------- #
# Collecteur principal
# --------------------------------------------------------------------------- #


class MetricsCollector:
    """
    Collecteur singleton *par nom de variante*.

    Exemple
    -------
    ```python
    mc = MetricsCollector("baseline")
    mc.add(prompt, latency, tokens)
    mc.to_json("baseline.jsonl")
    print(mc.summary())
    ```
    """

    _instances: Dict[str, "MetricsCollector"] = {}

    # --------------------------------------------------------------------- #
    # Construction / singleton
    # --------------------------------------------------------------------- #

    def __new__(cls, name: str):  # pylint: disable=unused-argument
        if name in cls._instances:
            return cls._instances[name]
        inst = super().__new__(cls)
        cls._instances[name] = inst
        return inst

    def __init__(self, name: str) -> None:
        # initialise une seule fois (si déjà init => noop)
        if hasattr(self, "_initialised"):
            return
        self.name = name
        self._samples: List[_Sample] = []
        self._initialised = True  # noqa: SLF001

    # --------------------------------------------------------------------- #
    # Ajout de mesures
    # --------------------------------------------------------------------- #

    def add(
        self,
        prompt: str,
        latency: float,
        tokens: int,
        memory_mb: Optional[float] = None,
        power_w: Optional[float] = None,
    ) -> None:
        """Ajoute 1 échantillon brut."""
        samp = _Sample(
            prompt=prompt,
            latency=latency,
            tokens=tokens,
            memory_mb=memory_mb if memory_mb is not None else math.nan,
            power_w=power_w if power_w is not None else math.nan,
        )
        self._samples.append(samp)

    # --------------------------------------------------------------------- #
    # Agrégation
    # --------------------------------------------------------------------- #

    def summary(self) -> Dict[str, Any]:
        """Statistiques p50/p95 + moyennes."""
        if not self._samples:
            return {"name": self.name, "count": 0}

        lats = [s.latency for s in self._samples]
        tpss = [s.tokens / s.latency for s in self._samples]
        mems = [s.memory_mb for s in self._samples if not math.isnan(s.memory_mb)]
        pows = [s.power_w for s in self._samples if not math.isnan(s.power_w)]

        def safe_mean(vals: List[float]) -> float:
            return stats.mean(vals) if vals else float("nan")

        def safe_max(vals: List[float]) -> float:
            return max(vals) if vals else float("nan")

        return {
            "name": self.name,
            "count": len(self._samples),
            # latence
            "latency_p50": _percentile(lats, 50),
            "latency_p95": _percentile(lats, 95),
            "latency_mean": safe_mean(lats),
            "latency_max": safe_max(lats),
            # throughput
            "tps_p50": _percentile(tpss, 50),
            "tps_p95": _percentile(tpss, 95),
            "tps_mean": safe_mean(tpss),
            # mémoire
            "memory_max": safe_max(mems),
            # puissance
            "power_mean": safe_mean(pows),
        }

    # --------------------------------------------------------------------- #
    # Exports
    # --------------------------------------------------------------------- #

    def to_json(self, path: str | Path) -> Path:
        """
        Écrit toutes les lignes en JSONL.  
        Renvoie le `Path` absolu créé.
        """
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            for s in self._samples:
                f.write(json.dumps(s.as_dict(), ensure_ascii=False) + "\n")
        return p

    # ------------------------------------------------------------------ #
    # Méthodes statiques
    # ------------------------------------------------------------------ #

    @staticmethod
    def dump_all() -> Dict[str, Dict[str, Any]]:
        """Retourne le résumé de toutes les variantes présentes."""
        return {name: inst.summary() for name, inst in MetricsCollector._instances.items()}

    @staticmethod
    def reset_all() -> None:
        """Efface *tous* les collecteurs – utile pour les tests unitaires."""
        MetricsCollector._instances.clear()
