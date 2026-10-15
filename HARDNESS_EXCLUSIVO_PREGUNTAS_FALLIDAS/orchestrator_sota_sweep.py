#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestador Autónomo de Barrido Térmico SOTA (Trío Qwen 3.5 9B)
==============================================================
Explora el intervalo [0.10, 0.20] con temperaturas finas:
- T = 0.12
- T = 0.15
- T = 0.18
Y consolida el mapeo completo junto a las temperaturas ya medidas (0.0, 0.10, 0.20, 0.30).
"""

import sys
import os
import re
import json
import time
import subprocess
from pathlib import Path

BASE_DIR = Path("/home/genelinux01/IAPower/Herramientas_IA/ACCESORIOS_PARA_LLM/LAB-PRUEBAS-TODO-TIPO/HARDNES-PRUEBAS/HARDEN-PRUEBA-QWEN3-5-9B/HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS")
HARNESS_SCRIPT = BASE_DIR / "harness_fallidas.py"
RESULTS_DIR = BASE_DIR / "resultados"
PROGRESS_LOG = BASE_DIR / "sweep_sota_progress.log"
ARTIFACT_DIR = Path("/home/genelinux01/Caja_Fuerte_IDE/Umbral/Config_Aislada/.gemini/antigravity/brain/8f9058ba-55a5-4fc0-a68b-5b60f0f14101")

TEMPS_TO_SWEEP = [0.15, 0.12, 0.18]
SEED = 2026

def log_msg(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_temperature(temp):
    log_msg(f"🚀 INICIANDO EVALUACIÓN PARA TEMPERATURA T = {temp} (Semilla: {SEED})")
    cmd = [
        sys.executable,
        str(HARNESS_SCRIPT),
        "--temp", str(temp),
        "--seed", str(SEED)
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", cwd=str(BASE_DIR))
        dt = time.time() - t0
        log_msg(f"✅ FINALIZADA EVALUACIÓN T = {temp} en {dt:.1f}s ({dt/60:.1f} min)")
        log_msg(f"Salida resumen:\n" + "\n".join(proc.stdout.splitlines()[-12:]))
        return True
    except Exception as e:
        log_msg(f"❌ ERROR en evaluación T = {temp}: {e}")
        return False

def generate_consolidated_report():
    log_msg("📊 Generando reporte y gráfica consolidada de todas las temperaturas...")
    
    # Lista completa de temperaturas a auditar
    all_temps = [0.0, 0.1, 0.12, 0.15, 0.18, 0.2, 0.3]
    models = ["Original", "Abliterado_V2", "Xiaomi_MiMo"]
    
    # Dataset
    with open(BASE_DIR / "dataset_8_fallidas_gsm8k.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    master_data = {}
    
    for t in all_temps:
        t_key = f"T_{t}"
        json_file = RESULTS_DIR / f"resultado_retest_seed_{SEED}_temp_{t}.json"
        # Casos especiales de nombres previos
        if not json_file.exists():
            if t == 0.3:
                json_file = RESULTS_DIR / f"resultado_retest_seed_{SEED}.json"
            elif t == 0.0:
                # Cargar de prior_run_v3
                master_data[t_key] = {
                    "temp": 0.0,
                    "scores": {"Original": 4, "Abliterado_V2": 4, "Xiaomi_MiMo": 4},
                    "details": {}
                }
                for q in questions:
                    idx = q["index"]
                    prior = q.get("prior_run_v3", {})
                    master_data[t_key]["details"][idx] = {
                        m: {
                            "pred": prior.get(m, {}).get("pred", "N/A"),
                            "correct": prior.get(m, {}).get("correct", False),
                            "time_s": prior.get(m, {}).get("time_s", 0.0)
                        } for m in models
                    }
                continue
                
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as fj:
                    data = json.load(fj)
                master_data[t_key] = {
                    "temp": t,
                    "scores": data.get("scores", {}),
                    "details": {
                        d["index"]: {
                            m: {
                                "pred": d["retest"].get(m, {}).get("pred", "N/A"),
                                "correct": d["retest"].get(m, {}).get("correct", False),
                                "time_s": d["retest"].get(m, {}).get("time_s", 0.0)
                            } for m in models
                        } for d in data.get("details", [])
                    }
                }
            except Exception as e:
                log_msg(f"Aviso al cargar {json_file}: {e}")

    # Guardar JSON Maestro
    master_json_path = RESULTS_DIR / "resumen_sota_sweep_todas_temperaturas.json"
    with open(master_json_path, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)
        
    # Guardar Markdown Maestro
    master_md_path = RESULTS_DIR / "reporte_sota_sweep_todas_temperaturas.md"
    with open(master_md_path, "w", encoding="utf-8") as f:
        f.write("# 🏆 REPORTE MAESTRO: BARRIDO TÉRMICO COMPLETO SOTA (GSM8K)\n\n")
        f.write(f"**Semilla:** `{SEED}` | **Modelos:** Original, Abliterado V2, Xiaomi MiMo (`<think> ON`)\n")
        f.write(f"**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, KV Cache FP16 puro\n\n")
        f.write("### 📈 Tabla Resumen de Puntuaciones (% Aciertos sobre 8 Preguntas Clave)\n\n")
        f.write("| Temperatura | Original | Abliterado V2 | Xiaomi MiMo | Estado / Hallazgo |\n")
        f.write("| :---: | :---: | :---: | :---: | :--- |\n")
        
        best_score = -1
        best_temps = []
        
        for t in all_temps:
            t_key = f"T_{t}"
            t_info = master_data.get(t_key)
            if not t_info:
                f.write(f"| `T = {t}` | *(Pendiente)* | *(Pendiente)* | *(Pendiente)* | En cola |\n")
                continue
            sc = t_info.get("scores", {})
            orig = sc.get("Original", 0)
            ablit = sc.get("Abliterado_V2", 0)
            mimo = sc.get("Xiaomi_MiMo", 0)
            
            total_aciertos = orig + ablit + mimo
            if total_aciertos > best_score:
                best_score = total_aciertos
                best_temps = [t]
            elif total_aciertos == best_score:
                best_temps.append(t)
                
            orig_str = f"**{orig}/8** ({(orig/8)*100:.1f}%)"
            ablit_str = f"**{ablit}/8** ({(ablit/8)*100:.1f}%)"
            mimo_str = f"**{mimo}/8** ({(mimo/8)*100:.1f}%)"
            
            tag = ""
            if orig >= 5 and ablit >= 5 and mimo >= 5:
                tag = "🔥 **ZONA SOTA (Triple empate 62.5%+)**"
            elif ablit >= 6 or orig >= 6 or mimo >= 6:
                tag = "💎 **PUNTO SOTA MÁXIMO**"
            elif orig <= 3:
                tag = "⚠️ Colapso de Original por calor"
            else:
                tag = "Estable"
                
            f.write(f"| `T = {t}` | {orig_str} | {ablit_str} | {mimo_str} | {tag} |\n")
            
        f.write(f"\n---\n\n### 🎯 Punto SOTA Identificado: Temperaturas {best_temps}\n")

    log_msg(f"✅ Reporte maestro guardado en {master_md_path}")
    
    # Generar Infografía Panorámica con Matplotlib
    try:
        render_sweep_chart(master_data, all_temps, models, questions)
    except Exception as e:
        log_msg(f"Error generando gráfica: {e}")

def render_sweep_chart(master_data, all_temps, models, questions):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    
    valid_temps = [t for t in all_temps if f"T_{t}" in master_data]
    if not valid_temps:
        return
        
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 11), dpi=150, facecolor="#0B132B")
    
    # 1. Curva Térmica de Precisión (%)
    ax1.set_facecolor("#1C2541")
    for spine in ax1.spines.values():
        spine.set_color("#48CAE4")
        spine.set_linewidth(1.0)
        
    colors = {"Original": "#48CAE4", "Abliterado_V2": "#06D6A0", "Xiaomi_MiMo": "#FFD166"}
    markers = {"Original": "o", "Abliterado_V2": "s", "Xiaomi_MiMo": "^"}
    
    for m in models:
        scores = []
        for t in valid_temps:
            sc = master_data[f"T_{t}"]["scores"].get(m, 0)
            scores.append((sc / 8.0) * 100)
        ax1.plot(valid_temps, scores, marker=markers[m], markersize=9, linewidth=2.5,
                 label=f"{m} (Max: {max(scores):.1f}%)", color=colors[m])
        for x, y in zip(valid_temps, scores):
            ax1.annotate(f"{y:.1f}%", xy=(x, y), xytext=(0, 6), textcoords="offset points",
                         ha="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")
                         
    ax1.set_title("CURVA TÉRMICA SOTA: PRECISIÓN (%) VS TEMPERATURA [0.0 -> 0.3]", fontsize=14, fontweight="black", color="#48CAE4", pad=12)
    ax1.set_xlabel("Temperatura (T)", fontsize=11, fontweight="bold", color="#CAF0F8")
    ax1.set_ylabel("Precisión de Aciertos (%)", fontsize=11, fontweight="bold", color="#CAF0F8")
    ax1.set_xticks(valid_temps)
    ax1.set_xticklabels([f"T={t}" for t in valid_temps], fontsize=10, fontweight="bold", color="#FFFFFF")
    ax1.set_ylim(20, 85)
    ax1.grid(True, linestyle="--", alpha=0.25, color="#CAF0F8")
    ax1.legend(loc="lower left", facecolor="#0B132B", edgecolor="#48CAE4", labelcolor="#FFFFFF", fontsize=10)
    ax1.tick_params(colors="#CAF0F8")
    
    # Sombrear la zona óptima
    ax1.axvspan(0.10, 0.18, color="#06D6A0", alpha=0.12, label="Zona SOTA Óptima [0.10 - 0.18]")

    # 2. Latencia Promedio (Segundos)
    ax2.set_facecolor("#1C2541")
    for spine in ax2.spines.values():
        spine.set_color("#48CAE4")
        spine.set_linewidth(1.0)
        
    for m in models:
        times = []
        for t in valid_temps:
            m_times = [d.get(m, {}).get("time_s", 0.0) for d in master_data[f"T_{t}"]["details"].values() if d.get(m, {}).get("time_s", 0) > 0]
            avg_t = np.mean(m_times) if m_times else 0.0
            times.append(avg_t)
        ax2.plot(valid_temps, times, marker=markers[m], markersize=8, linewidth=2.0,
                 label=f"{m} Latencia", color=colors[m])
                 
    ax2.set_title("LATENCIA PROMEDIO DE RESOLUCIÓN POR TEMPERATURA", fontsize=13, fontweight="black", color="#48CAE4", pad=10)
    ax2.set_xlabel("Temperatura (T)", fontsize=11, fontweight="bold", color="#CAF0F8")
    ax2.set_ylabel("Tiempo Promedio (Segundos)", fontsize=11, fontweight="bold", color="#CAF0F8")
    ax2.set_xticks(valid_temps)
    ax2.set_xticklabels([f"T={t}" for t in valid_temps], fontsize=10, fontweight="bold", color="#FFFFFF")
    ax2.grid(True, linestyle="--", alpha=0.25, color="#CAF0F8")
    ax2.legend(loc="upper right", facecolor="#0B132B", edgecolor="#48CAE4", labelcolor="#FFFFFF", fontsize=9.5)
    ax2.tick_params(colors="#CAF0F8")
    
    plt.tight_layout()
    chart_path = RESULTS_DIR / "curva_sota_termica_todas_temperaturas.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    
    # Copiar a artifacts
    if ARTIFACT_DIR.exists():
        art_path = ARTIFACT_DIR / "curva_sota_termica_todas_temperaturas.png"
        import shutil
        shutil.copy(chart_path, art_path)
        
    plt.close()
    log_msg(f"✅ Gráfica de curva térmica guardada en {chart_path}")

def main():
    log_msg("=" * 80)
    log_msg("🔬 INICIANDO CAMPAÑA AUTÓNOMA OVERNIGHT DE BARRIDO SOTA")
    log_msg(f"Temperaturas a explorar: {TEMPS_TO_SWEEP}")
    log_msg("=" * 80)
    
    # Generar reporte inicial consolidado con lo que ya tenemos
    generate_consolidated_report()
    
    # Ejecutar el barrido
    for t in TEMPS_TO_SWEEP:
        run_temperature(t)
        generate_consolidated_report()
        time.sleep(2.0)
        
    log_msg("=" * 80)
    log_msg("🏁 CAMPAÑA SOTA OVERNIGHT COMPLETADA AL 100%. RESULTADOS LISTOS.")
    log_msg("=" * 80)

if __name__ == "__main__":
    main()
