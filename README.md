# 🧪 Qwen 3.5 9B Family: Suites Oficiales de Razonamiento GSM8K
### Evaluación Exhaustiva: Qwen 3.5 9B Original vs. Abliterado V2 vs. Xiaomi MiMo-V2.6-Distill

Repositorio oficial con los experimentos, datasets íntegros, scripts ejecutables de inferencia (*test harnesses*), bitácoras técnicas, gráficas de auditoría y 330 archivos de evidencia empírica generados en local sobre hardware **NVIDIA GeForce RTX 5080 Laptop GPU**.

---

## 🏆 1. Examen Completo de 100 Preguntas GSM8K (Benchmark Insignia - Versión 3)

**Fechas de Ejecución:** 13 al 14 de Octubre de 2026  
**Ubicación en el Repositorio:** [`VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/`](./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/)  
**Harness Utilizado:** `harness_runner_v3.py`  
**Dataset Oficial:** 100 preguntas secuenciales de OpenAI GSM8K ([`datasets/gsm8k_test_hf.jsonl`](./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/datasets/gsm8k_test_hf.jsonl))  
**Parámetros:** Contexto = `18,000 tokens` (`-c 18000`) | Salida Máx = `16,000 tokens` (`-n 16000`) | KV Cache = **FP16 puro** | Temp = `0.0` (determinista) | Timeout = `600s`  
**Cuantización Evaluada:** **100% Estrictamente Q8_0** para todos los modelos participantes.

### 📊 Tabla de Resultados Oficiales (100 Preguntas)

| Puesto | Modelo Evaluado | Cuantización | Aciertos / Total | Precisión | Tiempo Total | Tiempo Promedio / Pregunta | Longitud de Razonamiento |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Qwen 3.5 9B Abliterado V2** | Q8_0 | **96 / 100** | **96.0%** | 99.4 min *(5,963 s)* | 59.63 s | 1,800 – 4,000 tokens |
| 🥇 | **Qwen 3.5 9B Original (Alibaba)** | Q8_0 | **96 / 100** | **96.0%** | 101.0 min *(6,058 s)* | 60.58 s | 1,800 – 3,500 tokens |
| 🥇⚡ | **Xiaomi MiMo-V2.6-Distill** | Q8_0 | **96 / 100** | **96.0%** | **8.4 min *(503 s)*** | ⚡ **5.03 s *(12x más veloz)*** | **150 – 400 tokens** |

### 📈 Archivos de Evidencia del Examen de 100 Preguntas:
* **Reporte Detallado Pregunta a Pregunta:** [`resultados/reporte_100_gsm8k_trio.md`](./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/reporte_100_gsm8k_trio.md)
* **Datos Estructurados en JSON:** [`resultados/resultados_100_gsm8k_trio.json`](./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/resultados_100_gsm8k_trio.json)
* **Gráficas de Auditoría Generadas:**  
  * [`resultados/grafica_auditoria_fallos_100_gsm8k.png`](./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/grafica_auditoria_fallos_100_gsm8k.png)
  * [`resultados/grafica_aislamiento_fallos_gsm8k.png`](./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/grafica_aislamiento_fallos_gsm8k.png)
* **Trazas Crudas (300 archivos de log):** Ubicadas en `VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/evidencia/q{001..100}_{Original,Abliterado_V2,Xiaomi_MiMo}.log`.

---

## ⚡ 2. Réplica y Verificación Estridente (10 Tareas Salteadas de 10 en 10)

**Fecha de Ejecución:** 15 de Octubre de 2026  
**Ubicación en el Repositorio:** [`VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/`](./VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/)  
**Harness Utilizado:** `harness_runner.py` / `run_harness.sh`  
**Entorno de Software Actualizado:** **Ollama v0.40.4** oficial en producción + `llama.cpp` v0.6.0 (commit `b42b7e6d3`)  
**Parámetros:** Contexto = `18,000 tokens` (`-c 18000`) | Salida Máx = `16,384 tokens` (`-n 16384`) | Prefijo = `<|im_start|>assistant\n<think>\n` | KV Cache = `q4_0`  
**Dataset:** Tareas `[1, 11, 21, 31, 41, 51, 61, 71, 81, 91]` del conjunto de prueba GSM8K.

### 📊 Resultados de la Réplica (15 Octubre 2026)

| Modelo Evaluado | Cuantización | Aciertos Auditados | Precisión | Tiempo Total | Tiempo Promedio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Qwen 3.5 9B Original** | Q8_0 | **9 / 10** | **90.0%** | 528.5 s (~8.8 min) | 52.85 s |
| **Qwen 3.5 9B Abliterado V2** | Q8_0 | **9 / 10** | **90.0%** | 586.2 s (~9.7 min) | 58.62 s |
| **Xiaomi MiMo-V2.6-Distill** | Q8_0 | **9 / 10** | **90.0%** | ⚡ **74.6 s (~1.2 min)** | ⚡ **7.46 s (7.4x más veloz)** |

* **Evidencias Crudas (30 archivos):** [`VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/evidencia/`](./VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/evidencia/)
* **Reporte en Markdown:** [`VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/resultados/reporte_strided_10_comparativo_16k.md`](./VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/resultados/reporte_strided_10_comparativo_16k.md)
* **Dataset JSON:** [`VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/benchmark_gsm8k_strided10_completo.json`](./VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/benchmark_gsm8k_strided10_completo.json)

---

## 🔬 3. Gran Conclusión Científica: ¿Es MiMo más inteligente?

> **NO. Xiaomi MiMo no posee mayor inteligencia ni superioridad cognitiva sobre Qwen 3.5 9B Original ni sobre Qwen 3.5 9B Abliterado V2.**
> 
> * En el examen completo de **100 preguntas**, los tres modelos empataron exactamente en **96.0%** (96 de 100 problemas resueltos con éxito).
> * En la prueba de muestreo de **10 tareas**, los tres modelos empataron exactamente en **90.0%**.
> * **La falacia de los benchmarks tradicionales:** Cuando se evalúa con cortes de salida bajos (ej. 1,024 tokens), Original y Abliterado parecen "fallar" porque sus cadenas `<think>` profundas son interrumpidas antes de llegar al resultado final. Al otorgarles el techo adecuado (**16,000 / 16,384 tokens**), resuelven la matemática a la perfección.
> * **La verdadera ventaja de MiMo:** Es la **eficiencia extrema**. Al estar destilado por Xiaomi para sintetizar pasos lógicos en 150–400 tokens, concluye la misma tarea **12 veces más rápido en el lote de 100 preguntas** (8.4 minutos vs 100 minutos), con una huella mínima de consumo eléctrico y memoria KV.

---

## 🛠️ 4. Entorno de Hardware y Requisitos de Reproducibilidad

* **GPU:** NVIDIA GeForce RTX 5080 Laptop GPU (16 GB GDDR7 VRAM, 100% offload con `-ngl 99`).
* **CPU:** Intel Core Ultra (P-Cores aislados mediante `taskset -c 0-7` para evitar latencia de E-cores).
* **Motor Local:** `llama.cpp` oficial v0.6.0 (commit `b42b7e6d3`), ejecutado bajo **Ollama v0.40.4**.
* **Modelos Evaluados (Bóveda LLM Local):**
  * `Qwen3.5-9B-original-Q8_0.gguf`
  * `Qwen3.5-9B_ABLITERADO_V2-Q8_0.gguf`
  * `Qwen3.5-9B-xiaomi-Q8_0.gguf`

---

## 🔗 5. Repositorios de Pesos en Hugging Face

* **Qwen 3.5 9B Abliterado V2 (Repositorio Base):**  
  👉 [`HALO117MC/Qwen3.5-9B-Abliterated-V2`](https://huggingface.co/HALO117MC/Qwen3.5-9B-Abliterated-V2)
* **Qwen 3.5 9B Abliterado V2 (Colección GGUF Q8_0):**  
  👉 [`HALO117MC/Qwen3.5-9B-Abliterated-V2-GGUF`](https://huggingface.co/HALO117MC/Qwen3.5-9B-Abliterated-V2-GGUF)
