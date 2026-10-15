# 📋 BITÁCORA OFICIAL DE HARDNESS — VERSIÓN 3

**Fecha de Creación:** 13 de Octubre de 2026  
**Ubicación Canónica:** `./VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/`

---

## 1. Razón del Salto a Versión 3 (Historial y Evolución)

- **Versión 1 (`VERSION_1_2026-10-13_TRIPLE_COMPARATIVA`):**
  - **Prueba piloto:** 15 preguntas GSM8K.
  - **Límite:** `-n 1024` tokens, `-c 4096`.
  - **Hallazgo:** El modelo Xiaomi MiMo obtuvo 80.0% (12/15) en 5s por pregunta. Los modelos Original y Abliterado obtuvieron 60.0% (9/15). Se identificó que el modelo Original no fallaba en la matemática en sí, sino por **Reasoning Token Budget Exhaustion**: su cadena interna `<think>` superaba los 1,024 tokens y se cortaba antes de imprimir la respuesta final.

- **Versión 2 (`VERSION_2_2026-10-13_DATASET_COMPLETO_100_GSM8K`):**
  - Se expandió a `-n 2048` / `-n 8192` y contexto `-c 16384` con caché KV en Q4_0.
  - Evaluó 7 preguntas (Original 6/7, Xiaomi 7/7, Abliterado 7/7). En la pregunta 3, el razonamiento profundo tomó 135 segundos y el usuario solicitó detener para otorgar el máximo presupuesto posible sin restricciones.

- **Versión 3 (Esta Ejecución):**
  - **Presupuesto de Salida:** `-n 16000` (16,000 tokens de salida).
  - **Ventana de Contexto:** `-c 18000` (18,000 tokens).
  - **Precisión KV Cache:** **FP16 puro** (sin `-ctk q4_0` ni `-ctv q4_0`). Esto elimina cualquier ruido de redondeo o error por cuantización en el cálculo de atención durante razonamientos multi-etapa.
  - **Evidencia Completa:** Se crea el directorio `evidencia/` donde cada respuesta cruda generada por cada modelo en cada pregunta queda guardada con timestamp y métricas (`evidencia/qXXX_<modelo>.log`).

---

## 2. Parámetros Técnicos y Gobernanza de Hardware

| Parámetro | Valor Configurado | Justificación Técnica |
| :--- | :--- | :--- |
| **Aceleración GPU** | NVIDIA GeForce RTX 5080 (16 GB VRAM) | 100% de capas y tensores (`-ngl 99`) en GPU. |
| **VRAM Total Ocupada** | ~11.5 GB / 16.3 GB | Modelo Q8_0 (~9.2 GB) + KV Cache FP16 18k (~2.3 GB). Deja >4.8 GB de margen de seguridad en VRAM. |
| **KV Cache Precision** | **FP16** | Cero degradación de atención en cadenas de pensamiento largas. |
| **Afinidad de Proceso** | `taskset -c 0-7` (P-cores Intel 275HX) | Despacho y llamadas CUDA libres de latencia de E-cores. |
| **Aislamiento de Contexto** | 100% Estricto (`contexto = 0`) | Subproceso independiente por pregunta; Linux y CUDA liberan la memoria al terminar cada problema. |
| **Temperatura** | `0.0` (Greedy Decoding) | Determinismo absoluto estándar de la industria. |
| **Timeout por Consulta** | 600 segundos (10 minutos) | Tiempo suficiente para que cualquier cadena de pensamiento de miles de tokens concluya sin ser interrumpida. |

---

## 3. Modelos Evaluados

1. **Original:** `Qwen3.5-9B-original-Q8_0.gguf` (9.2 GB)
2. **Abliterado V2:** `Qwen3.5-9B_ABLITERADO_V2-Q8_0.gguf` (9.2 GB)
3. **Xiaomi MiMo:** `Qwen3.5-9B-xiaomi-Q8_0.gguf` (8.9 GB, destilado)

---

## 4. Registro y Resultados Finales (Conclusión de 100 Preguntas)

- **Dataset:** 100 preguntas oficiales de GSM8K (`gsm8k_test_hf.jsonl`).
- **Resultados en tiempo real:** `resultados/resultados_100_gsm8k_trio.json`.
- **Reporte dinámico:** `resultados/reporte_100_gsm8k_trio.md`.
- **Trazas completas:** `evidencia/q{001..100}_{Original,Abliterado_V2,Xiaomi_MiMo}.log`.

### 🏆 Podio Final Oficial:
| Puesto | Modelo | Aciertos | Precisión | Tiempo Total | Tiempo Promedio/Pregunta |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 🥇 | **Qwen 3.5 9B Abliterado V2** | **96 / 100** | **96.0%** | 99.4 min (5,963s) | 59.63s |
| 🥇 | **Qwen 3.5 9B Original (Alibaba)** | **96 / 100** | **96.0%** | 101.0 min (6,058s) | 60.58s |
| 🥇⚡ | **Xiaomi MiMo-V2.6 (Max Reasoning)** | **96 / 100** | **96.0%** | **8.4 min (503s)** | **5.03s (12x más rápido)** |

