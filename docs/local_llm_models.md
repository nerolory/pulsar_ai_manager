# Локальные LLM модели для Pulsar AI Manager

## Рекомендации по моделям для каждого tier

### Very Light Tier (4GB RAM, 2 CPU cores)
**Рекомендуемые модели:**
- **TinyLlama-1.1B-Chat-v1.0** - 1.1B параметров
  - RAM: ~2-3GB (quantized 4-bit)
  - Контекст: 2048 tokens
  - Лицензия: Apache 2.0
  - Производительность: ~5-10 tok/s на CPU
  
- **Phi-3-mini-2.7B** (если есть 4GB+ RAM)
  - RAM: ~3-4GB (quantized 4-bit)
  - Контекст: 4096 tokens
  - Лицензия: MIT
  - Производительность: ~8-15 tok/s на CPU

### Light Tier (8GB RAM, 4 CPU cores)
**Рекомендуемые модели:**
- **Phi-3-mini-3.8B** - 3.8B параметров
  - RAM: ~4-6GB (quantized 4-bit)
  - Контекст: 4096 tokens
  - Лицензия: MIT
  - Производительность: ~10-20 tok/s на CPU
  
- **Qwen-1.5-1.8B-Chat** - 1.8B параметров
  - RAM: ~2-3GB (quantized 4-bit)
  - Контекст: 32768 tokens
  - Лицензия: Apache 2.0
  - Производительность: ~15-25 tok/s на CPU

### Medium Tier (16GB RAM, 6+ CPU cores или GPU)
**Рекомендуемые модели:**
- **Phi-3-medium-4B** - 4B параметров
  - RAM: ~6-8GB (quantized 4-bit)
  - VRAM: ~4-6GB (GPU)
  - Контекст: 4096 tokens
  - Лицензия: MIT
  - Производительность: ~20-40 tok/s на CPU, ~50-100 tok/s на GPU
  
- **Qwen-1.5-7B-Chat** - 7B параметров
  - RAM: ~8-12GB (quantized 4-bit)
  - VRAM: ~6-8GB (GPU)
  - Контекст: 32768 tokens
  - Лицензия: Apache 2.0
  - Производительность: ~15-30 tok/s на CPU, ~60-120 tok/s на GPU

## Требования к зависимостям

Для запуска локальных LLM потребуются:
- `torch` - PyTorch для инференса
- `transformers` - Hugging Face Transformers
- `accelerate` - для оптимизации инференса
- `bitsandbytes` - для 4-bit квантования (опционально)
- `llama-cpp-python` - для GGUF моделей (опционально)
- `psutil` - для проверки системных ресурсов (уже есть)
- `py-cpuinfo` - для проверки CPU features (опционально)
- `GPUtil` - для проверки GPU (опционально)

## Форматы моделей

Рекомендуемые форматы:
1. **GGUF** - для llama.cpp (лучше для CPU)
2. **Safetensors** - для Transformers (лучше для GPU)
3. **PyTorch** - стандартный формат

## Стратегия квантования

Для снижения требований к RAM:
- **4-bit (Q4_K_M)** - оптимальный баланс качества/размера
- **8-bit** - если 4-bit дает плохое качество
- **FP16** - если есть достаточно VRAM

## Источники моделей

- Hugging Face: https://huggingface.co/models
- TheBloke (quantized models): https://huggingface.co/TheBloke
- Microsoft Phi-3: https://huggingface.co/microsoft
- Qwen: https://huggingface.co/Qwen
