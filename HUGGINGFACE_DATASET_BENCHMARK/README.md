---
annotations_creators:
- machine-generated
- expert-generated
language:
- en
language_creators:
- found
license: mit
multilinguality:
- monolingual
size_categories:
- 1K<n<10K
source_datasets:
- gsm8k
task_categories:
- question-answering
- text-generation
pretty_name: "Qwen 3.5 9B GSM8K Benchmark & Thermodynamic SOTA Audit"
tags:
- evaluation
- benchmark
- gsm8k
- qwen
- qwen3.5
- reasoning
- thinking-tokens
- thermal-sweep
- gguf
- deepseek-judge
- llama.cpp
configs:
- config_name: default
  data_files:
  - split: test_100q
    path: data/gsm8k_100q_suite_results.json
  - split: sota_sweep
    path: data/gsm8k_sota_sweep_all_temperatures.json
---

# 🚀 Qwen 3.5 9B GSM8K Benchmark & Thermodynamic SOTA Sweep Audit

<p align="center">
  👤 <b>Developer (GitHub):</b> <a href="https://github.com/irving2017cloud"><b>@irving2017cloud</b></a> • 📂 <b>Official GitHub Harness Repo:</b> <a href="https://github.com/irving2017cloud/Qwen3.5-9B-Reasoning-Benchmarks"><b>Qwen3.5-9B-Reasoning-Benchmarks</b></a>
</p>

This repository contains the complete, forensic evaluation datasets, raw execution logs, throughput metrics, and high-resolution performance infographics for the **Qwen 3.5 9B** LLM family across three architectural variants:

1. **Qwen 3.5 9B Original** (`Q8_0` GGUF) — Base reference model.
2. **Qwen 3.5 9B Abliterado V2** (`Q8_0` GGUF) — **Partial / Conservative Tensor Surgery** (see technical disclosure below).
3. **Qwen 3.5 9B Xiaomi MiMo** (`Q8_0` GGUF) — Distilled reasoning model with `<think>` tags.

---

### ⚠️ Technical Disclosure on Abliterado V2 (Cirugía Tensorial Parcial ~10%)
> **Crucial Architecture Note:** The *Abliterado V2* variant evaluated in this benchmark is **not** an aggressive or fully abliterated model. It is a **conservative tensor surgery** where only approximately **10% of refusal directional activations** were removed from the weight tensors.
> 
> Because this surgical intervention was intentionally kept at ~10%, the underlying mathematical and reasoning manifolds were preserved almost intact. This empirical finding explains why *Abliterado V2* tracked so closely with *Original* (both reaching 96.0% accuracy on the full 100-question GSM8K suite) and why its thermodynamic behavior in temperature sweeps remained stable without representation collapse.

---

## 🖥️ Hardware Telemetry & Test Environment

All benchmarks were executed locally under strict hardware and software governance:

| Component | Specification | Configuration |
| :--- | :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 5080 Laptop GPU (16 GB GDDR7) | 100% offload (`-ngl 99`), Driver 615.78.08, CUDA 12.8 |
| **CPU** | Intel(R) Core(TM) Ultra 9 275HX (24 Cores) | Core affinity via `taskset -c 0-7` (P-cores) |
| **KV Cache** | Pure FP16 (Zero quantization degradation) | Context `-c 18000`, Output `-n 16000` |
| **Isolation** | Strict Zero-State Isolation | Independent sub-process per query (`contexto = 0`) |
| **Inference Engine** | `llama.cpp` (b0-unknown build) | GGUF Q8_0 quantizations |
| **Judge Auditor** | DeepSeek V3 Math Validation Harness | Automated mathematical equivalence verification |

---

## 📊 Key Findings & Temperature Dynamics

### 1. 100-Question GSM8K Full Suite (Version 3)
- **Triple Tie at 96.0% (96/100 correct answers)** across all three models.
- **Xiaomi MiMo $12\times$ Throughput Advantage:**
  - Original: **101.0 minutes total** (~60.6s per question).
  - Abliterado V2: **99.4 minutes total** (~59.6s per question).
  - Xiaomi MiMo: **8.4 minutes total** (~5.0s per question) with identical 96.0% accuracy.
- **Reasoning Budget:** Zero truncations occurred. All 300 inferences terminated naturally with `<|im_end|>`.

### 2. Thermodynamic Temperature Sweep on Hard Boundary Failures
Retesting the 8 boundary failed questions (Q13, Q38, Q46, Q63, Q74, Q76, Q86, Q94) across $T \in [0.00, 0.10, 0.12, 0.15, 0.18, 0.20, 0.30]$ with seed `2026`:

| Temperatura | Original | Abliterado V2 (~10% Cirugía) | Xiaomi MiMo | Estado / Hallazgo Dinámico |
| :---: | :---: | :---: | :---: | :--- |
| **$T = 0.00$** | 4/8 (50.0%) | 4/8 (50.0%) | 4/8 (50.0%) | Determinismo base (Greedy decoding) |
| **$T = 0.10$** | **5/8 (62.5%)** | **5/8 (62.5%)** | **5/8 (62.5%)** | 🔥 **Zona Dulce Conjunta (Triple empate 62.5%)** |
| **$T = 0.12$** | 5/8 (62.5%) | 4/8 (50.0%) | 5/8 (62.5%) | Estabilidad de MiMo y Original |
| **$T = 0.15$** | 4/8 (50.0%) | 3/8 (37.5%) | 5/8 (62.5%) | Valle térmico para variantes densas |
| **$T = 0.18$** | **6/8 (75.0%)** 👑 | 4/8 (50.0%) | 5/8 (62.5%) | 💎 **PUNTO SOTA MÁXIMO (Original alcanza 75%)** |
| **$T = 0.20$** | 4/8 (50.0%) | **5/8 (62.5%)** | 5/8 (62.5%) | Rebote de Abliterado V2 a 62.5% |
| **$T = 0.30$** | 3/8 (37.5%) | 4/8 (50.0%) | 5/8 (62.5%) | ⚠️ Ruido excesivo / Degradación de Original |

#### 🎯 Preguntas Específicas Resueltas en el Punto SOTA ($T = 0.18$):
- **Original ($T=0.18$):** Resuelve con éxito **Q38, Q46, Q63, Q74, Q76 y Q86** (6/8 aciertos).
- **Xiaomi MiMo:** Resuelve consistentemente **Q94** (vallas de atletismo), siendo el **único modelo capaz de resolverla** en todo el espectro de temperaturas, manteniendo una latencia constante de **~5.2 segundos**.

---

## 📈 Visual Infographics & Performance Charts

### 1. Curva SOTA Térmica ($T \in [0.00, 0.30]$)
Trayectoria de precisión a través de las 7 temperaturas evaluadas:
![Curva SOTA Térmica](https://huggingface.co/datasets/HALO117MC/Qwen3.5-9B-GSM8K-Thermal-Benchmark-Audit/resolve/main/figures/curva_sota_termica_todas_temperaturas.png)

### 2. Matriz Comparativa de 4 Tests Históricos (GSM8K)
Evolución completa desde la versión piloto de 15 preguntas hasta el barrido fino SOTA:
![Matriz Comparativa 4 Tests](https://huggingface.co/datasets/HALO117MC/Qwen3.5-9B-GSM8K-Thermal-Benchmark-Audit/resolve/main/figures/matriz_comparativa_4_tests_gsm8k.png)

### 3. Comparativa Integral de los 3 Tests Principales
![Matriz Comparativa 3 Tests](https://huggingface.co/datasets/HALO117MC/Qwen3.5-9B-GSM8K-Thermal-Benchmark-Audit/resolve/main/figures/matriz_comparativa_3_tests_gsm8k.png)

### 4. Aislamiento de Fallos y Auditoría de 100 Preguntas
Mapas forenses de las preguntas erróneas y consistencia entre modelos:
![Aislamiento de Fallos](https://huggingface.co/datasets/HALO117MC/Qwen3.5-9B-GSM8K-Thermal-Benchmark-Audit/resolve/main/figures/grafica_aislamiento_fallos_gsm8k.png)
![Auditoría de Fallos 100 Preguntas](https://huggingface.co/datasets/HALO117MC/Qwen3.5-9B-GSM8K-Thermal-Benchmark-Audit/resolve/main/figures/grafica_auditoria_fallos_100_gsm8k.png)

---

## 📁 Repository Structure

```
├── README.md                                  # Dataset Card & Documentation
├── figures/                                   # High-resolution benchmark infographics
│   ├── curva_sota_termica_todas_temperaturas.png
│   ├── matriz_comparativa_4_tests_gsm8k.png
│   ├── matriz_comparativa_3_tests_gsm8k.png
│   ├── grafica_aislamiento_fallos_gsm8k.png
│   └── grafica_auditoria_fallos_100_gsm8k.png
├── reports/                                   # Detailed markdown audit reports
│   ├── reporte_sota_sweep_todas_temperaturas.md
│   ├── reporte_100_gsm8k_trio.md
│   ├── bitacora_metodologica_v3.md
│   └── reporte_retest_temp_*.md
├── data/                                      # JSON structured test results
│   ├── gsm8k_100q_suite_results.json
│   ├── gsm8k_sota_sweep_all_temperatures.json
│   ├── dataset_8_fallidas_gsm8k.json
│   └── sweep_tables/                          # Per-temperature evaluation outputs
└── raw_logs/                                  # 444+ raw execution logs with token throughput
    ├── gsm8k_100q_suite_logs/                 # 300 full test traces (100 questions x 3 models)
    └── thermal_sweep_logs/                    # 144 sweep logs across seeds and temperatures
```

---

## 🔬 Citation

```bibtex
@misc{qwen35_gsm8k_thermal_audit_2026,
  author = {HALO117MC},
  title = {Qwen 3.5 9B GSM8K Benchmark and Thermodynamic SOTA Sweep Audit},
  year = {2026},
  publisher = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/HALO117MC/Qwen3.5-9B-GSM8K-Thermal-Benchmark-Audit}}
}
```
