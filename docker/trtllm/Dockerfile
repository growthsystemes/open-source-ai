# Dockerfile pour l'environnement TensorRT-LLM optimisé
FROM nvcr.io/nvidia/tensorrt_llm:24.03-py3

# Arguments de build
ARG MODEL_ID=meta-llama/Llama-2-7b-chat-hf
ARG QUANT_MODE=fp16
ARG HF_HOME=/workspace/.cache/huggingface

# Variables d'environnement
ENV MODEL_ID=${MODEL_ID}
ENV TRT_PRECISION=${QUANT_MODE}
ENV QUANT_MODE=${QUANT_MODE}
ENV HF_HOME=${HF_HOME}
ENV PYTHONPATH=/workspace:$PYTHONPATH

# Retour en root pour installations
USER root

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Création d'un utilisateur non-root
RUN useradd -ms /bin/bash -u 1000 user && \
    mkdir -p /workspace /workspace/.cache /workspace/engines && \
    chown -R user:user /workspace

# Copie du code source et scripts
COPY --chown=user:user scripts/ /workspace/scripts/
COPY --chown=user:user inference_optim_llm/ /workspace/inference_optim_llm/
COPY --chown=user:user docker/trtllm/build_engine.sh /workspace/

# Installation du package local
WORKDIR /workspace
RUN pip install --no-cache-dir -e .

# Configuration des permissions
RUN chmod +x /workspace/build_engine.sh

# Téléchargement du modèle et compilation de l'engine au build
# (long mais image prête à utiliser)
USER user
RUN python scripts/download_model.py --model_id ${MODEL_ID} --output_dir ${HF_HOME}/models && \
    python -m inference_optim_llm.cli build ${MODEL_ID} \
        --precision ${QUANT_MODE} \
        --max-input-len 4096 \
        --max-output-len 2048

# Point d'entrée pour l'exécution
ENTRYPOINT ["python", "scripts/run_trtllm.py"]
CMD ["--prompts-file", "data/prompts.txt"]
