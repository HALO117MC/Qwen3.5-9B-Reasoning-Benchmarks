#!/usr/bin/env python3
"""
Script de Sanitización y Empaquetado para Hugging Face Dataset
Ofusca datos personales y rutas locales privadas, preservando la telemetría de hardware,
rendimiento, latencias, tokens por segundo y veredictos de auditoría DeepSeek.
"""

import os
import re
import shutil
import json
from pathlib import Path

BASE_LAB = Path("./HARDEN-PRUEBA-QWEN3-5-9B")
EXPORT_DIR = BASE_LAB / "HUGGINGFACE_DATASET_BENCHMARK"

# Subdirectorios del dataset
DIRS = {
    "root": EXPORT_DIR,
    "figures": EXPORT_DIR / "figures",
    "reports": EXPORT_DIR / "reports",
    "data": EXPORT_DIR / "data",
    "sweep_tables": EXPORT_DIR / "data" / "sweep_tables",
    "v3_logs": EXPORT_DIR / "raw_logs" / "gsm8k_100q_suite_logs",
    "sweep_logs": EXPORT_DIR / "raw_logs" / "thermal_sweep_logs",
}

for d in DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

REPLACEMENTS = [
    ("./models/Qwen3.5-9B/GGUF/", "models/"),
    ("./", "benchmark/"),
    ("./artifacts/8f9058ba-55a5-4fc0-a68b-5b60f0f14101/", "figures/"),
    ("/workspace/Caja_Fuerte_IDE/Umbral/Config_Aislada/.gemini/antigravity/", "artifacts/"),
    ("/workspace/IAPower/Herramientas_IA/", "/workspace/"),
    ("/workspace/", "/workspace/"),
    ("developer", "researcher"),
]

def sanitize_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text

print("1. Copiando y sanitizando figuras e infografías...")
figures_src = [
    BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/curva_sota_termica_todas_temperaturas.png",
    BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/matriz_comparativa_4_tests_gsm8k.png",
    BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/matriz_comparativa_3_tests_gsm8k.png",
    BASE_LAB / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/grafica_aislamiento_fallos_gsm8k.png",
    BASE_LAB / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/grafica_auditoria_fallos_100_gsm8k.png",
]
for src in figures_src:
    if src.exists():
        shutil.copy2(src, DIRS["figures"] / src.name)
        print(f"   [OK] Figura: {src.name}")

print("2. Copiando y sanitizando reportes...")
reports_src = [
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/reporte_sota_sweep_todas_temperaturas.md", "reporte_sota_sweep_todas_temperaturas.md"),
    (BASE_LAB / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/reporte_100_gsm8k_trio.md", "reporte_100_gsm8k_trio.md"),
    (BASE_LAB / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/BITACORA_VERSION_3.md", "bitacora_metodologica_v3.md"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/reporte_comparativo_retest_seed_2026_temp_0.1.md", "reporte_retest_temp_0.10.md"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/reporte_comparativo_retest_seed_2026_temp_0.12.md", "reporte_retest_temp_0.12.md"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/reporte_comparativo_retest_seed_2026_temp_0.15.md", "reporte_retest_temp_0.15.md"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/reporte_comparativo_retest_seed_2026_temp_0.18.md", "reporte_retest_temp_0.18.md"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/reporte_comparativo_retest_seed_2026_temp_0.2.md", "reporte_retest_temp_0.20.md"),
]
for src, dst_name in reports_src:
    if src.exists():
        content = src.read_text(encoding="utf-8")
        sanitized = sanitize_text(content)
        (DIRS["reports"] / dst_name).write_text(sanitized, encoding="utf-8")
        print(f"   [OK] Reporte: {dst_name}")

print("3. Copiando y sanitizando tablas JSON...")
json_src = [
    (BASE_LAB / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/resultados_100_gsm8k_trio.json", DIRS["data"] / "gsm8k_100q_suite_results.json"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados/resumen_sota_sweep_todas_temperaturas.json", DIRS["data"] / "gsm8k_sota_sweep_all_temperatures.json"),
    (BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/dataset_8_fallidas_gsm8k.json", DIRS["data"] / "dataset_8_fallidas_gsm8k.json"),
]
for src, dst in json_src:
    if src.exists():
        content = src.read_text(encoding="utf-8")
        sanitized = sanitize_text(content)
        dst.write_text(sanitized, encoding="utf-8")
        print(f"   [OK] JSON: {dst.name}")

sweep_jsons = list((BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/resultados").glob("resultado_retest_seed_2026*.json"))
for src in sweep_jsons:
    content = src.read_text(encoding="utf-8")
    sanitized = sanitize_text(content)
    dst = DIRS["sweep_tables"] / src.name
    dst.write_text(sanitized, encoding="utf-8")
print(f"   [OK] Tablas de sweep térmico copiadas: {len(sweep_jsons)}")

print("4. Copiando y sanitizando logs crudos de Version 3 (100 preguntas x 3 modelos = 300 logs)...")
v3_logs_dir = BASE_LAB / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/evidencia"
count_v3 = 0
for f in v3_logs_dir.glob("*.log"):
    content = f.read_text(encoding="utf-8", errors="replace")
    sanitized = sanitize_text(content)
    (DIRS["v3_logs"] / f.name).write_text(sanitized, encoding="utf-8")
    count_v3 += 1
print(f"   [OK] Logs V3 sanitizados: {count_v3}")

print("5. Copiando y sanitizando logs crudos de barrido térmico (144 logs)...")
sweep_logs_dir = BASE_LAB / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS/evidencia"
count_sweep = 0
for f in sweep_logs_dir.glob("*.log"):
    content = f.read_text(encoding="utf-8", errors="replace")
    sanitized = sanitize_text(content)
    (DIRS["sweep_logs"] / f.name).write_text(sanitized, encoding="utf-8")
    count_sweep += 1
print(f"   [OK] Logs Sweep sanitizados: {count_sweep}")

print("\n--- RESUMEN DE SANITIZACIÓN ---")
print(f"Destino canónico: {EXPORT_DIR}")
print(f"Figuras: {len(list(DIRS['figures'].glob('*')))}")
print(f"Reportes: {len(list(DIRS['reports'].glob('*')))}")
print(f"Datos JSON: {len(list(DIRS['data'].glob('*.*'))) + len(list(DIRS['sweep_tables'].glob('*')))}")
print(f"Logs V3: {count_v3}")
print(f"Logs Sweep: {count_sweep}")
print("Total archivos preparados:", sum(len(list(p.glob('*'))) for p in DIRS.values()))
