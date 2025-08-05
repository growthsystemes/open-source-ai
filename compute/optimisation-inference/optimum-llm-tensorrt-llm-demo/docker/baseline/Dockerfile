# Dockerfile pour l'environnement baseline (HuggingFace/PyTorch)
FROM nvcr.io/nvidia/pytorch:24.03-py3

# Arguments de build
ARG MODEL_ID=meta-llama/Llama-2-7b-chat-hf
ARG HF_HOME=/workspace/.cache/huggingface

# Variables d'environnement
ENV MODEL_ID=${MODEL_ID}
ENV HF_HOME=${HF_HOME}
ENV PYTHONPATH=/workspace:$PYTHONPATH

# Installation des dépendances système et Python
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -ms /bin/bash -u 1000 user && \
    mkdir -p /workspace /workspace/.cache && \
    chown -R user:user /workspace

# Copie du code source
COPY --chown=user:user scripts/ /workspace/scripts/
COPY --chown=user:user inference_optim_llm/ /workspace/inference_optim_llm/

# Installation du package local
WORKDIR /workspace
RUN pip install --no-cache-dir -e .

# Téléchargement du modèle HF au build (image autonome)
RUN python scripts/download_model.py --model_id ${MODEL_ID} --output_dir ${HF_HOME}/models

# Configuration utilisateur et point d'entrée
USER user
ENTRYPOINT ["python", "scripts/run_baseline.py"]
CMD ["--prompts-file", "data/prompts.txt"]
