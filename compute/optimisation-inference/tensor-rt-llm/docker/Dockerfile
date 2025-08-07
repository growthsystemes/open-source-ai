# Dockerfile pour TensorRT-LLM benchmarking
FROM nvcr.io/nvidia/tensorrt-llm/devel:1.0.0rc6

# Mise à jour et installation des dépendances supplémentaires
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installation des packages Python supplémentaires pour le benchmarking
RUN pip install --no-cache-dir \
    matplotlib \
    seaborn \
    pandas \
    psutil \
    nvidia-ml-py3

# Création des répertoires de travail
WORKDIR /workspace
RUN mkdir -p /workspace/models /workspace/engines /workspace/results /workspace/scripts

# Copie des scripts
COPY scripts/ /workspace/scripts/
RUN chmod +x /workspace/scripts/*.sh

# Variables d'environnement
ENV PYTHONPATH=/workspace
ENV CUDA_VISIBLE_DEVICES=0

# Point d'entrée
ENTRYPOINT ["/bin/bash"]
