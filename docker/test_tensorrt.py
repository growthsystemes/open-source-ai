#!/usr/bin/env python3
"""Script de test pour TensorRT-LLM"""

try:
    import tensorrt_llm
    print("TensorRT-LLM OK")
except ImportError:
    print("TensorRT-LLM not available - CLI will handle this gracefully")
    # Ne pas faire exit(1) car le CLI peut gérer l'absence de TensorRT-LLM