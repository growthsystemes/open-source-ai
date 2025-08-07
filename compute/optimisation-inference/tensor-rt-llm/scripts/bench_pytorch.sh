#!/bin/bash
set -e

# Script de benchmark PyTorch pour TinyLlama
echo "=== Benchmark PyTorch (référence) ==="

MODEL_NAME="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
MODEL_DIR="data/models/tinyllama"
RESULTS_DIR="data/results"
PYTORCH_RESULTS="$RESULTS_DIR/pytorch_benchmark.json"

mkdir -p "$RESULTS_DIR"

echo "Installation des dépendances pour PyTorch..."
pip install --no-cache-dir transformers torch accelerate datasets matplotlib seaborn pandas psutil nvidia-ml-py3

echo "Lancement du benchmark PyTorch..."

python3 << 'EOF'
import torch
import time
import json
import psutil
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from datetime import datetime
import numpy as np

def get_gpu_memory():
    """Récupère l'utilisation mémoire GPU"""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return info.used / 1024**3  # GB
    except:
        return 0

def benchmark_pytorch(model_dir, num_iterations=10):
    """Benchmark du modèle PyTorch"""
    print("Chargement du modèle PyTorch...")
    
    # Chargement du modèle et tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Prompts de test longs et complexes pour maximiser l'impact TensorRT
    test_prompts = [
        """You are an AI assistant specialized in advanced technology. Please provide a comprehensive explanation of how artificial intelligence systems work, including the fundamental concepts of machine learning, deep learning, neural networks, and their real-world applications. Discuss the differences between supervised, unsupervised, and reinforcement learning approaches. Also explain the current limitations and future potential of AI technology in various industries such as healthcare, finance, transportation, and education.""",
        
        """Write a detailed technical analysis of quantum computing systems and their potential impact on modern cryptography and computational science. Explain the fundamental principles of quantum mechanics that enable quantum computing, including superposition, entanglement, and quantum interference. Discuss the current state of quantum hardware, the challenges in building stable quantum computers, and how quantum algorithms like Shor's algorithm and Grover's algorithm could revolutionize fields such as cybersecurity, drug discovery, and optimization problems.""",
        
        """Provide an in-depth explanation of climate change mechanisms, including the greenhouse effect, carbon cycle disruptions, and feedback loops in Earth's climate system. Analyze the role of human activities such as fossil fuel combustion, deforestation, and industrial processes in accelerating global warming. Discuss the observed and projected impacts on ecosystems, weather patterns, sea levels, and human societies. Include information about mitigation strategies, renewable energy technologies, carbon capture methods, and international climate policies.""",
        
        """Explain the complex biological processes involved in cellular metabolism, DNA replication, and protein synthesis. Describe how genetic information flows from DNA to RNA to proteins, and how this central dogma of molecular biology enables life functions. Discuss the role of enzymes, the structure and function of different types of RNA, and how genetic mutations can affect cellular processes. Also explain modern biotechnology applications such as CRISPR gene editing, genetic engineering, and personalized medicine.""",
        
        """Analyze the evolution and current state of blockchain technology and distributed ledger systems. Explain the cryptographic principles underlying blockchain security, including hash functions, digital signatures, and consensus mechanisms like proof-of-work and proof-of-stake. Discuss various applications beyond cryptocurrency, such as smart contracts, supply chain management, decentralized finance (DeFi), and non-fungible tokens (NFTs). Address the scalability challenges, energy consumption concerns, and regulatory considerations facing blockchain adoption."""
    ]
    
    results = {
        "backend": "pytorch",
        "model": "TinyLlama-1.1B-Chat",
        "timestamp": datetime.now().isoformat(),
        "iterations": num_iterations,
        "metrics": {
            "latency_ms": [],
            "throughput_tokens_per_sec": [],
            "memory_usage_gb": [],
            "input_tokens": [],
            "output_tokens": []
        },
        "summary": {}
    }
    
    print(f"Exécution de {num_iterations} itérations...")
    
    for i in range(num_iterations):
        prompt = test_prompts[i % len(test_prompts)]
        
        # Tokenisation
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_length = inputs['input_ids'].shape[1]
        
        # Mesure de la mémoire avant génération
        memory_before = get_gpu_memory()
        
        # Génération avec mesure du temps
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                max_new_tokens=200,  # Plus de tokens pour maximiser l'impact TensorRT
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        end_time = time.time()
        
        # Calcul des métriques
        latency_ms = (end_time - start_time) * 1000
        output_length = outputs.shape[1] - input_length
        total_tokens = outputs.shape[1]
        throughput = total_tokens / (end_time - start_time)
        memory_after = get_gpu_memory()
        
        # Stockage des résultats
        results["metrics"]["latency_ms"].append(latency_ms)
        results["metrics"]["throughput_tokens_per_sec"].append(throughput)
        results["metrics"]["memory_usage_gb"].append(memory_after)
        results["metrics"]["input_tokens"].append(input_length)
        results["metrics"]["output_tokens"].append(output_length)
        
        print(f"Itération {i+1}/{num_iterations}: {latency_ms:.1f}ms, {throughput:.1f} tokens/s")
    
    # Calcul des statistiques de résumé
    results["summary"] = {
        "avg_latency_ms": np.mean(results["metrics"]["latency_ms"]),
        "std_latency_ms": np.std(results["metrics"]["latency_ms"]),
        "avg_throughput_tokens_per_sec": np.mean(results["metrics"]["throughput_tokens_per_sec"]),
        "std_throughput_tokens_per_sec": np.std(results["metrics"]["throughput_tokens_per_sec"]),
        "avg_memory_usage_gb": np.mean(results["metrics"]["memory_usage_gb"]),
        "max_memory_usage_gb": max(results["metrics"]["memory_usage_gb"]),
        "total_input_tokens": sum(results["metrics"]["input_tokens"]),
        "total_output_tokens": sum(results["metrics"]["output_tokens"])
    }
    
    return results

# Exécution du benchmark
model_dir = os.environ.get('MODEL_DIR', 'data/models/tinyllama')
results = benchmark_pytorch(model_dir)

# Sauvegarde des résultats
output_file = 'data/results/pytorch_benchmark.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n=== Résultats PyTorch ===")
print(f"Latence moyenne: {results['summary']['avg_latency_ms']:.1f} ± {results['summary']['std_latency_ms']:.1f} ms")
print(f"Débit moyen: {results['summary']['avg_throughput_tokens_per_sec']:.1f} ± {results['summary']['std_throughput_tokens_per_sec']:.1f} tokens/s")
print(f"Mémoire GPU utilisée: {results['summary']['avg_memory_usage_gb']:.2f} GB")
print(f"Résultats sauvegardés dans: {output_file}")

EOF

echo "=== Benchmark PyTorch terminé ==="
