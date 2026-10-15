# 📋 Bitácora Técnica de Versión: V1 (2026-10-13)

**Identificador de Versión:** `VERSION_1_2026-10-13_TRIPLE_COMPARATIVA`  
**Ubicación:** `/home/genelinux01/IAPower/Herramientas_IA/ACCESORIOS_PARA_LLM/LAB-PRUEBAS-TODO-TIPO/HARDNES-PRUEBAS/HARDEN-PRUEBA-QWEN3-5-9B/VERSION_1_2026-10-13_TRIPLE_COMPARATIVA/`  
**Fecha de Ejecución:** 13 de Octubre de 2026  
**Responsable:** Antigravity AI & Químico de Tensores  

---

## 🎯 1. Objetivo del Harness V1
Diseñar y estandarizar el primer harness de evaluación rigurosa para la familia **Qwen 3.5 9B**, integrando por primera vez el modelo destilado **Xiaomi MiMo-V2.6-Distill-Qwen-9B**, comparándolo contra el modelo **Original (Alibaba)** y la variante **Abliterada V2 (Cirugía de Tensores)**.

---

## ⚙️ 2. Especificaciones de Diseño y Parámetros del Harness

| Parámetro | Valor Configurado | Justificación Técnica |
| :--- | :--- | :--- |
| **GPU Target** | NVIDIA RTX 5080 Laptop (16 GB) | Alojamiento al 100% en VRAM (`-ngl 99`) para Q8_0 (~9.5 GB ocupados) |
| **CPU Pinning** | `taskset -c 0-7` | Afinidad estricta a los Performance Cores (P-cores) para máxima tasa de prompt evaluation |
| **Contexto (-c)** | `4096` (Sanity: `2048`, HMMT: `32768`) | Longitud de ventana balanceada para evaluación matemática y de razonamiento |
| **Generación (-n)**| `1024` tokens | Margen para cadenas de pensamiento largas (`<think>`) |
| **Batch (-b / -ub)**| `19 / 19` | Configuración probada en el Quirófano para evitar jitter de latencia |
| **KV Cache Quant** | `-ctk q4_0 -ctv q4_0` | Compresión en memoria para permitir contextos extendidos sin saturar la VRAM |
| **MTP Bypass** | `--no-mtp` | Exclusión de la capa fantasma residual de Xiaomi MiMo (corrige fallo de tensor `blk.32.attn_norm.weight`) |
| **Temperatura** | `0.0` (Benchmark) / `0.2` (Sanity) | Inferencia determinista y reproducible |

---

## 📊 3. Datasets Oficiales Incorporados

1. **`openai/gsm8k` (Hugging Face Datasets):**
   * Archivo: `datasets/gsm8k_test_hf.jsonl`
   * Propósito: Medición de razonamiento aritmético paso a paso con verificación exacta de `#### <valor>`.
2. **`MathArena/hmmt_feb_2025` (Hugging Face Datasets):**
   * Archivo: `datasets/hmmt_feb_2025_hf.jsonl`
   * Propósito: Evaluación en problemas de competición matemática de Harvard-MIT (criterio oficial reportado por Alibaba).

---

## 📈 4. Hallazgos y Rendimiento Observado

* **Velocidad de Generación:**
  * **Xiaomi MiMo Q8_0:** **62.6 a 64.8 tokens/s** (promedio de resolución por problema: **4 a 7 segundos**).
  * **Qwen 3.5 9B Original Q8_0:** **61.2 a 64.7 tokens/s** (promedio de resolución: **18 a 26 segundos**, debido a trazas de pensamiento más redundantes).
  * **Qwen 3.5 9B Abliterado V2 Q8_0:** **61.8 tokens/s** (promedio de resolución: **17 a 20 segundos**).
* **Capacidad de Resolución de Problemas:**
  * Xiaomi MiMo demostró mayor precisión y concisión en problemas trampa (ejemplo Pregunta 3: Original y Abliterado respondieron incorrectamente 80,000, mientras que Xiaomi MiMo calculó con precisión 70,000 en sólo 6.9s).
