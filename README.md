# 🧪 Qwen 3.5 9B Family: Test Harness & Reasoning Benchmarks
### Evaluando Qwen 3.5 9B Original vs. Abliterado V2 vs. Xiaomi MiMo-V2.6-Distill

Repositorio oficial con los experimentos, datasets, scripts de inferencia, bitácoras y evidencias empíricas de la suite de evaluación matemática y de razonamiento **GSM8K**.

---

## 🏆 1. Resultados Consolidados: ¿Es Xiaomi MiMo realmente superior?

Se realizó una evaluación comparativa determinista de los 3 modelos en cuantización **Q8_0** ejecutados en local sobre hardware idéntico y con **Ollama v0.40.4 / llama.cpp v0.6.0**:

| Modelo | Cuantización | Aciertos (Auditados) | Precisión | Tiempo Total (10 tareas) | Tiempo Medio / Tarea | Tokens Promedio Razonamiento |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Qwen 3.5 9B Original** | Q8_0 | **9 / 10** | **90.0%** | 528.5 s (~8.8 min) | 52.85 s | 1,800 – 3,500 tokens |
| **Qwen 3.5 9B Abliterado V2** | Q8_0 | **9 / 10** | **90.0%** | 586.2 s (~9.7 min) | 58.62 s | 2,000 – 4,000 tokens |
| **Xiaomi MiMo-V2.6-Distill** | Q8_0 | **9 / 10** | **90.0%** | ⚡ **74.6 s (~1.2 min)** | ⚡ **7.46 s (7.4x más veloz)** | **150 – 400 tokens** |

### 💡 Conclusiones Técnicas Principales:
1. **Misma Capacidad Cognitiva:** Xiaomi MiMo **no es más inteligente** ni posee mayor tasa de acierto que el modelo base de Alibaba o el modelo Abliterado V2. Ambos modelos base empatan en el **90%** de precisión matemática.
2. **El Cuello de Botella de los 1,024 Tokens:** Las afirmaciones previas sobre "fallos" del modelo Original o Abliterado se debían a evaluaciones con límites artificiales de 1,024 tokens. Como sus cadenas de razonamiento (`<think>`) son profundas y minuciosas, se truncaban antes de escribir el resultado final. Al expandir la ventana a **16,384 tokens de salida**, demostraron precisión matemática absoluta.
3. **La Verdadera Superioridad de MiMo:** Su ventaja no es de razonamiento sino de **eficiencia de destilación**. Resuelve las mismas tareas con un 90% menos de tokens y en una séptima parte del tiempo (1.2 minutos vs casi 10 minutos).

---

## ⚙️ 2. Entorno de Ejecución y Hardware

* **GPU:** NVIDIA GeForce RTX 5080 Laptop GPU (16 GB GDDR7 VRAM, 100% offload con `-ngl 99`).
* **CPU:** Intel Core Ultra (P-Cores aislados con `taskset -c 0-7`).
* **Motor de Inferencia:** `llama.cpp` oficial v0.6.0 (commit `b42b7e6d3`), integrado en **Ollama v0.40.4**.
* **Ventana de Contexto (`-c`):** `18,000 tokens`.
* **Límite de Generación (`-n`):** `16,384 tokens`.
* **Configuración de Memoria:** KV Cache cuantizado a `q4_0` (`-ctk q4_0 -ctv q4_0`), Flash Attention activo.
* **Prefijo Forzado:** `<|im_start|>assistant\n<think>\n` para activación determinista del razonamiento en todas las variantes.

---

## 📂 3. Estructura del Repositorio

```text
HARDEN-PRUEBA-QWEN3-5-9B/
├── VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/  # 🌟 Experimento Principal Vigente
│   ├── datasets/                                # Dataset con 10 tareas muestreadas de 10 en 10
│   ├── evidencia/                               # Salidas crudas completas generadas por los 3 modelos
│   ├── resultados/                              # Reportes comparativos en Markdown
│   ├── benchmark_gsm8k_strided10_completo.json  # Telemetría, fechas, configuración y dataset en JSON
│   ├── config_harness.json                      # Configuración de inferencia (18k / 16k)
│   ├── harness_runner.py                        # Script ejecutor de pruebas automatizadas
│   └── run_harness.sh                           # Lanzador con taskset para núcleos P
├── VERSION_1_2026-10-13_TRIPLE_COMPARATIVA/      # Primera versión de evaluación
├── VERSION_2_2026-10-13_DATASET_COMPLETO_100_GSM8K/ # Evaluación sobre el dataset de 100 tareas
├── VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/   # Pruebas con ampliación de tokens
└── HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/       # Pruebas dirigidas en tareas con discrepancias
```

---

## 🔗 4. Modelos en Hugging Face

* **Qwen 3.5 9B Abliterado V2 (Safetensors / BF16):**  
  👉 [`HALO117MC/Qwen3.5-9B-Abliterated-V2`](https://huggingface.co/HALO117MC/Qwen3.5-9B-Abliterated-V2)
* **Qwen 3.5 9B Abliterado V2 (GGUF Q8_0):**  
  👉 [`HALO117MC/Qwen3.5-9B-Abliterated-V2-GGUF`](https://huggingface.co/HALO117MC/Qwen3.5-9B-Abliterated-V2-GGUF)
