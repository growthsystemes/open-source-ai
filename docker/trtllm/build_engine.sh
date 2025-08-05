#!/usr/bin/env bash
set -e
MODEL_ID=${MODEL_ID:-meta-llama/Llama-2-7b-chat-hf}
PREC=${TRT_PRECISION:-fp16}

python /opt/tensorrt_llm/examples/llama/convert_checkpoint.py   --model_dir ${MODEL_ID}   --output_dir /workspace/llama2_trtllm   --dtype ${PREC}

trtllm-build   --checkpoint_dir /workspace/llama2_trtllm   --output_dir /workspace/engines   --dtype ${PREC} --batch_size 1 --max_input_len 4096
