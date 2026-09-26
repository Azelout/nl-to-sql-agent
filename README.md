```  bash
uv run vllm serve Qwen/Qwen2.5-Coder-7B-Instruct \
    --port 8000 \
    --gpu-memory-utilization 0.80 \
    --max-model-len 4096 \
    --dtype bfloat16  
```
