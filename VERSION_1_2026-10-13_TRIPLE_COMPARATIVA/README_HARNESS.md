# 🧪 Test Harness: Qwen 3.5 9B & Xiaomi MiMo-V2.6-Distill-Qwen-9B

Ubicación oficial del Harness de Pruebas:
`./`

---

## ⚡ Particularidades Técnicas del Modelo

### 1. Arquitectura Híbrida: Gated DeltaNet + Gated Attention
* **Capas:** 32 capas troncales (layout: 3 bloques de atención lineal SSM Gated DeltaNet por cada 1 bloque de atención estándar Gated Attention).
* **Dimensiones de Atención Lineal:** 32 cabezas V (dim 128) y 16 cabezas QK (dim 128).
* **Interleaved MRoPE:** Requiere secciones de dimensión `[11, 11, 10, 0]`.
* **Soporte Binario:** Exige binarios de `llama.cpp` compilados con `llama_model_qwen35` implementado en `libllama.so`.

### 2. Saneamiento Crítico de MTP (Multi-Token Prediction)
* **El Problema:** El modelo destilado `XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B` conserva en su `config.json` el parámetro `"mtp_num_hidden_layers": 1`. Sin embargo, durante el entrenamiento SFT/destilación de Xiaomi, la cabeza MTP fue eliminada de los tensores `safetensors`.
* **La Solución:** Toda conversión y carga de GGUF debe utilizar la bandera `--no-mtp` para evitar que `llama.cpp` reserve una capa fantasma (capa 32/33) y lance el error: `check_tensor_dims: tensor 'blk.32.attn_norm.weight' not found`.

### 3. Asignación de Hardware y VRAM (RTX 5080 16GB)
* **Q8_0:** Ocupa **~9.5 GB de VRAM** (cabe al 100% en la GPU con `-ngl 99`), alcanzando entre **60 y 65 tokens/s**.
* **BF16:** Ocupa **~17.0 GB**, desbordando ligeramente a RAM del sistema (~38 tokens/s).
* **Parámetros Óptimos de KV Cache:** `-ctk q4_0 -ctv q4_0` con `-b 19 -ub 19` fijado a P-cores (`taskset -c 0-7`).

---

## 📂 Estructura del Harness

```text
HARDNES-PRUEBAS/
├── config_harness.json          # Configuración global de rutas, modelos y flags
├── datasets/                    # Datasets descargados desde Hugging Face
│   ├── gsm8k_test_hf.jsonl      # Test split oficial de openai/gsm8k
│   └── hmmt_feb_2025_hf.jsonl   # Benchmark oficial HMMT Feb 2025 (MathArena)
├── test_suite_sanity.py         # Sanity check rápido (<15 segundos)
├── harness_runner.py            # Evaluador configurable por flags
├── run_harness.sh               # Menú ejecutable interactivo
├── resultados/                  # Salidas JSON y reportes generados
└── README_HARNESS.md            # Esta documentación
```

---

## 🚀 Uso Rápido

### 1. Ejecutar Sanity Check
Comprueba en segundos que el modelo cargue en GPU y responda coherentemente:
```bash
/workspace/IAPower/Herramientas_IA/Cirugia_Tensores/venv/bin/python test_suite_sanity.py xiaomi_q8
```

### 2. Ejecutar Benchmark GSM8K (Hugging Face)
Evalúa preguntas matemáticas paso a paso y calcula precisión exacta:
```bash
/workspace/IAPower/Herramientas_IA/Cirugia_Tensores/venv/bin/python harness_runner.py --models xiaomi_q8 original_q8 --dataset gsm8k --samples 10
```

### 3. Ejecutar Benchmark HMMT (Olimpiada Matemática de Harvard-MIT)
```bash
/workspace/IAPower/Herramientas_IA/Cirugia_Tensores/venv/bin/python harness_runner.py --models xiaomi_q8 original_q8 --dataset hmmt_feb_2025 --samples 5
```
