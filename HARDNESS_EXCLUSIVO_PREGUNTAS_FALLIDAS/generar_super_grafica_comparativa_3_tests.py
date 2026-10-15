#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Gráfica Integral Comparativa Multi-Versión GSM8K (Trío Qwen 3.5 9B)
Compara:
- Test 1: GSM8K 100 Preguntas (Oficial V3) | Temp: 0.0 (Greedy)
- Test 2: Retest 8 Fallidas | Temp: 0.3 | Semilla: 2026
- Test 3: Retest 8 Fallidas | Temp: 0.1 | Semilla: 2026 (En vivo / dinámico)
"""

import os
import re
import json
import glob
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

BASE_DIR = Path("/home/genelinux01/IAPower/Herramientas_IA/ACCESORIOS_PARA_LLM/LAB-PRUEBAS-TODO-TIPO/HARDNES-PRUEBAS/HARDEN-PRUEBA-QWEN3-5-9B")
V3_RESULTS = BASE_DIR / "VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K" / "resultados" / "resultados_100_gsm8k_trio.json"
RETEST_DIR = BASE_DIR / "HARDNESS_EXCLUSIVO_PREGUNTAS_FALLIDAS"
RETEST_EVID = RETEST_DIR / "evidencia"
RETEST_T03 = RETEST_DIR / "resultados" / "resultado_retest_seed_2026.json"
DATASET_PATH = RETEST_DIR / "dataset_8_fallidas_gsm8k.json"

OUT_DIR_LAB = RETEST_DIR / "resultados"
OUT_DIR_ARTIFACT = Path("/home/genelinux01/Caja_Fuerte_IDE/Umbral/Config_Aislada/.gemini/antigravity/brain/8f9058ba-55a5-4fc0-a68b-5b60f0f14101")

def clean_output(raw_text):
    text = re.sub(r'\[\s*Prompt:.*?\]', '', raw_text, flags=re.DOTALL)
    if '<|im_start|>assistant' in text:
        text = text.split('<|im_start|>assistant', 1)[1]
    return text.strip()

def parse_model_response(raw_text):
    text = clean_output(raw_text)
    if "[End thinking]" in text:
        text = text.split("[End thinking]", 1)[1]
    elif "</think>" in text:
        text = text.split("</think>", 1)[1]
    text = text.strip()
    
    m = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text)
    if m:
        return m.group(1).replace(',', '').strip()
    m_boxed = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', text)
    if m_boxed:
        return m_boxed.group(1).replace(',', '').strip()
    ans_lines = [l.strip() for l in text.splitlines() if re.search(r'(?:\*\*Answer:?|Answer:)', l, re.IGNORECASE)]
    if ans_lines:
        line = ans_lines[-1]
        bold = re.findall(r'\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)\s*\*\*', line)
        if bold:
            return bold[-1].replace(',', '').strip()
        nums = re.findall(r'\$?(-?[\d,]+(?:\.\d+)?)', line)
        if nums:
            return nums[-1].replace(',', '').strip()
    bold_all = re.findall(r'\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)\s*\*\*', text)
    if bold_all:
        return bold_all[-1].replace(',', '').strip()
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line or 'exiting' in line.lower() or '===' in line:
            continue
        nums = re.findall(r'\$?(-?[\d,]+(?:\.\d+)?)', line)
        if nums:
            return nums[-1].replace(',', '').strip()
    return None

def compare_numbers(pred_str, gold_str):
    if pred_str is None or gold_str is None:
        return False
    try:
        p = float(str(pred_str).replace(',', '').strip())
        g = float(str(gold_str).replace(',', '').strip())
        return abs(p - g) < 1e-4
    except Exception:
        return str(pred_str).strip().lower() == str(gold_str).strip().lower()

def load_all_data():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    with open(RETEST_T03, "r", encoding="utf-8") as f:
        t03_data = json.load(f)
    t03_by_idx = {r["index"]: r for r in t03_data.get("details", [])}

    models = ["Original", "Abliterado_V2", "Xiaomi_MiMo"]
    master = []

    question_titles = {
        13: "Q13: Limonero Carlos ($90 costo)",
        38: "Q38: John Sets de Lego (13 sets)",
        46: "Q46: Blog Meredith (2/5 fracción)",
        63: "Q63: Pensión Marcy ($50k/40 años)",
        74: "Q74: Shiela Celulares (2% interés)",
        76: "Q76: Castillo Arena Luke (4 niveles)",
        86: "Q86: Manta Gene (23 a 34 años)",
        94: "Q94: Carrera Vallas Gerald (10% mejora)"
    }

    for item in questions:
        idx = item["index"]
        gold = item["gold"]
        q_row = {
            "index": idx,
            "title": question_titles.get(idx, f"Pregunta #{idx}"),
            "gold": gold,
            "tests": {
                "Test1_T00": {},
                "Test2_T03": {},
                "Test3_T01": {}
            }
        }

        # 1. Test 1 (T=0.0 de V3)
        prior = item.get("prior_run_v3", {})
        for m in models:
            pm = prior.get(m, {})
            q_row["tests"]["Test1_T00"][m] = {
                "pred": pm.get("pred", "N/A"),
                "correct": pm.get("correct", False),
                "time_s": pm.get("time_s", 0.0),
                "status": "DONE"
            }

        # 2. Test 2 (T=0.3 Retest)
        t03_entry = t03_by_idx.get(idx, {}).get("retest", {})
        for m in models:
            tm = t03_entry.get(m, {})
            q_row["tests"]["Test2_T03"][m] = {
                "pred": tm.get("pred", "N/A"),
                "correct": tm.get("correct", False),
                "time_s": tm.get("time_s", 0.0),
                "status": "DONE"
            }

        # 3. Test 3 (T=0.1 Retest en vivo)
        for m in models:
            log_pattern = RETEST_EVID / f"retest_q{idx:03d}_{m}_seed2026_temp0.1.log"
            if log_pattern.exists():
                with open(log_pattern, "r", encoding="utf-8", errors="replace") as fl:
                    raw = fl.read()
                time_m = re.search(r"Tiempo:\s*([\d\.]+)s", raw)
                dt = float(time_m.group(1)) if time_m else 0.0
                pred = parse_model_response(raw)
                ok = compare_numbers(pred, gold)
                q_row["tests"]["Test3_T01"][m] = {
                    "pred": pred if pred else "Err",
                    "correct": ok,
                    "time_s": dt,
                    "status": "DONE"
                }
            else:
                q_row["tests"]["Test3_T01"][m] = {
                    "pred": "...",
                    "correct": False,
                    "time_s": 0.0,
                    "status": "PENDING"
                }
        master.append(q_row)

    return master

def render_infographic(master):
    fig = plt.figure(figsize=(26, 17), dpi=150, facecolor="#0B132B")
    
    # Grid layout: Top Title (height 0.08), Main Matrix (height 0.58), Bottom Charts (height 0.28)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.09, 0.60, 0.31], width_ratios=[0.55, 0.45],
                          hspace=0.22, wspace=0.18, left=0.04, right=0.96, top=0.95, bottom=0.04)

    # ==========================
    # 1. HEADER BANNER
    # ==========================
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.axis("off")
    ax_head.set_facecolor("#0B132B")

    # Header decorative box
    head_box = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor="#1C2541", edgecolor="#48CAE4", linewidth=2.0)
    ax_head.add_patch(head_box)

    ax_head.text(0.02, 0.68, "AUDITORÍA COMPARATIVA GSM8K: TRÍO QWEN 3.5 9B (8 PREGUNTAS CLAVE)",
                 fontsize=20, fontweight="black", color="#FFFFFF", family="sans-serif")
    ax_head.text(0.02, 0.25, "Evolución por Temperatura: Test 1 (T=0.0 / V3 100 Qs)  vs  Test 2 (T=0.3 / Seed 2026)  vs  Test 3 (T=0.1 / Seed 2026)",
                 fontsize=12, fontweight="medium", color="#48CAE4", family="sans-serif")
    
    # Metadata tags on right
    ax_head.text(0.72, 0.68, "GPU: NVIDIA RTX 5080 Laptop (16GB)", fontsize=11, fontweight="bold", color="#72EFDD")
    ax_head.text(0.72, 0.40, "Contexto: 18,000 | Salida: 16,000 tokens", fontsize=10, color="#CAF0F8")
    ax_head.text(0.72, 0.15, "Precisión: FP16 KV Cache pura (Sin Q4)", fontsize=10, color="#90E0EF")

    # ==========================
    # 2. MAIN MATRIX DASHBOARD
    # ==========================
    ax_matrix = fig.add_subplot(gs[1, :])
    ax_matrix.axis("off")
    ax_matrix.set_facecolor("#0B132B")

    models = ["Original", "Abliterado_V2", "Xiaomi_MiMo"]
    model_labels = ["Original", "Abliterado V2", "Xiaomi MiMo\n(<think> ON)"]
    tests = [
        ("Test1_T00", "TEST 1: GSM8K 100 Qs\n(Temp = 0.0 | Greedy)", "#0077B6"),
        ("Test2_T03", "TEST 2: Retest 8 Fallidas\n(Temp = 0.3 | Seed 2026)", "#7209B7"),
        ("Test3_T01", "TEST 3: Retest 8 Fallidas\n(Temp = 0.1 | Seed 2026)", "#028090")
    ]

    num_rows = len(master) # 8
    # Coordinate system: X in [0, 1], Y in [0, 1]
    y_row_height = 0.88 / num_rows
    x_col_q_w = 0.19
    x_test_group_w = (1.0 - x_col_q_w - 0.02) / 3.0
    x_subcol_w = x_test_group_w / 3.0

    # Draw Column Headers
    y_hdr = 0.94
    # Question Header
    ax_matrix.text(x_col_q_w / 2.0, y_hdr + 0.02, "PREGUNTA (GSM8K)\n& VALOR GOLD ESPERADO",
                   fontsize=11, fontweight="bold", color="#CAF0F8", ha="center", va="center")

    # Test Groups Header
    for t_i, (t_key, t_title, t_col) in enumerate(tests):
        x_group_start = x_col_q_w + 0.01 + t_i * x_test_group_w
        # Header banner box
        hdr_rect = patches.FancyBboxPatch((x_group_start, y_hdr - 0.02), x_test_group_w - 0.008, 0.07,
                                          boxstyle="round,pad=0.01,rounding_size=0.015",
                                          facecolor=t_col, edgecolor="#FFFFFF", linewidth=1.0, alpha=0.85)
        ax_matrix.add_patch(hdr_rect)
        ax_matrix.text(x_group_start + (x_test_group_w - 0.008) / 2.0, y_hdr + 0.015, t_title,
                       fontsize=10.5, fontweight="black", color="#FFFFFF", ha="center", va="center")
        
        # Subheaders for models
        for m_i, m_lbl in enumerate(model_labels):
            x_sub = x_group_start + m_i * x_subcol_w
            ax_matrix.text(x_sub + x_subcol_w / 2.0, y_hdr - 0.045, m_lbl,
                           fontsize=9.5, fontweight="bold", color="#CAF0F8", ha="center", va="center")

    # Draw Rows
    for r_i, q in enumerate(master):
        y_pos = y_hdr - 0.075 - (r_i + 1) * y_row_height
        
        # Row zebra background
        row_bg = patches.Rectangle((0.005, y_pos), 0.99, y_row_height * 0.94,
                                   facecolor="#162238" if r_i % 2 == 0 else "#0F1A2E",
                                   edgecolor="#233554", linewidth=0.8)
        ax_matrix.add_patch(row_bg)

        # Question Title and Gold box
        ax_matrix.text(0.015, y_pos + y_row_height * 0.60, q["title"],
                       fontsize=10.5, fontweight="bold", color="#FFFFFF", va="center")
        ax_matrix.text(0.015, y_pos + y_row_height * 0.25, f"Esperado (Gold): {q['gold']}",
                       fontsize=9.5, fontweight="black", color="#FFD166", va="center")

        # Cells for each test and each model
        for t_i, (t_key, _, _) in enumerate(tests):
            x_group_start = x_col_q_w + 0.01 + t_i * x_test_group_w
            for m_i, m_name in enumerate(models):
                x_cell = x_group_start + m_i * x_subcol_w
                cell_data = q["tests"][t_key].get(m_name, {})
                status = cell_data.get("status", "PENDING")
                pred = str(cell_data.get("pred", "N/A"))
                correct = cell_data.get("correct", False)
                dt = cell_data.get("time_s", 0.0)

                # Cell styling
                if status == "PENDING":
                    c_bg = "#2B2D42"
                    c_border = "#4A4E69"
                    c_text = "#8D99AE"
                    icon_str = "[EN CURSO]"
                    dt_str = "esperando..."
                elif correct:
                    c_bg = "#064E3B" # Dark Emerald Green
                    c_border = "#10B981"
                    c_text = "#ECFDF5"
                    icon_str = f"[OK] Pred: {pred}"
                    dt_str = f"t: {dt:.1f}s"
                else:
                    c_bg = "#7F1D1D" # Dark Crimson Red
                    c_border = "#EF4444"
                    c_text = "#FEF2F2"
                    icon_str = f"[FAIL] Pred: {pred}"
                    dt_str = f"t: {dt:.1f}s"

                cell_rect = patches.FancyBboxPatch((x_cell + 0.002, y_pos + 0.005),
                                                   x_subcol_w - 0.004, y_row_height * 0.82,
                                                   boxstyle="round,pad=0.005,rounding_size=0.01",
                                                   facecolor=c_bg, edgecolor=c_border, linewidth=1.2)
                ax_matrix.add_patch(cell_rect)

                # Text inside cell
                ax_matrix.text(x_cell + x_subcol_w / 2.0, y_pos + y_row_height * 0.54, icon_str,
                               fontsize=9.5, fontweight="bold", color=c_text, ha="center", va="center")
                ax_matrix.text(x_cell + x_subcol_w / 2.0, y_pos + y_row_height * 0.22, dt_str,
                               fontsize=8.5, fontweight="medium", color="#94A3B8" if not correct else "#6EE7B7",
                               ha="center", va="center")

    # ==========================
    # 3. BOTTOM-LEFT: LATENCY COMPARISON BAR CHART
    # ==========================
    ax_bar = fig.add_subplot(gs[2, 0])
    ax_bar.set_facecolor("#1C2541")
    for spine in ax_bar.spines.values():
        spine.set_color("#48CAE4")
        spine.set_linewidth(1.0)

    # Average latencies across all 8 questions
    avg_times = {
        "Test 1 (T=0.0)": [145.9, 136.5, 5.0],
        "Test 2 (T=0.3)": [172.6, 169.7, 5.1],
        "Test 3 (T=0.1)": []
    }
    # Calculate Test 3 current avg
    t3_m_times = {"Original": [], "Abliterado_V2": [], "Xiaomi_MiMo": []}
    for q in master:
        for m in models:
            d = q["tests"]["Test3_T01"].get(m, {})
            if d.get("status") == "DONE" and d.get("time_s", 0) > 0:
                t3_m_times[m].append(d["time_s"])
    
    t3_avgs = [
        np.mean(t3_m_times["Original"]) if t3_m_times["Original"] else 0,
        np.mean(t3_m_times["Abliterado_V2"]) if t3_m_times["Abliterado_V2"] else 0,
        np.mean(t3_m_times["Xiaomi_MiMo"]) if t3_m_times["Xiaomi_MiMo"] else 0
    ]
    avg_times["Test 3 (T=0.1)"] = t3_avgs

    x_idx = np.arange(len(model_labels))
    bar_width = 0.24

    c_bars = ["#0077B6", "#7209B7", "#028090"]
    rects1 = ax_bar.bar(x_idx - bar_width, avg_times["Test 1 (T=0.0)"], bar_width, label="Test 1: V3 (T=0.0)", color=c_bars[0], edgecolor="#FFFFFF", alpha=0.9)
    rects2 = ax_bar.bar(x_idx, avg_times["Test 2 (T=0.3)"], bar_width, label="Test 2: Retest (T=0.3)", color=c_bars[1], edgecolor="#FFFFFF", alpha=0.9)
    rects3 = ax_bar.bar(x_idx + bar_width, avg_times["Test 3 (T=0.1)"], bar_width, label="Test 3: Retest (T=0.1 actual)", color=c_bars[2], edgecolor="#FFFFFF", alpha=0.9)

    ax_bar.set_xticks(x_idx)
    ax_bar.set_xticklabels(model_labels, fontsize=11, fontweight="bold", color="#FFFFFF")
    ax_bar.set_ylabel("Tiempo Promedio de Respuesta (Segundos)", fontsize=11, fontweight="bold", color="#CAF0F8")
    ax_bar.set_title("COMPARATIVA DE VELOCIDAD / LATENCIA PROMEDIO", fontsize=13, fontweight="black", color="#48CAE4", pad=10)
    ax_bar.grid(axis="y", linestyle="--", alpha=0.25, color="#CAF0F8")
    ax_bar.legend(loc="upper right", facecolor="#0B132B", edgecolor="#48CAE4", labelcolor="#FFFFFF", fontsize=9.5)
    ax_bar.tick_params(colors="#CAF0F8")

    # Add labels on top of bars
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax_bar.annotate(f"{height:.1f}s",
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#FFFFFF")

    # Note on MiMo speed
    ax_bar.text(2.0, 45, "Xiaomi MiMo es\n15x-30x más veloz\n(~5s por pregunta)",
                ha="center", fontsize=9.5, fontweight="black", color="#72EFDD",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#0B132B", edgecolor="#72EFDD", linewidth=1.2))

    # ==========================
    # 4. BOTTOM-RIGHT: ACCURACY SCORECARD ACROSS VERSIONS
    # ==========================
    ax_acc = fig.add_subplot(gs[2, 1])
    ax_acc.set_facecolor("#1C2541")
    for spine in ax_acc.spines.values():
        spine.set_color("#48CAE4")
        spine.set_linewidth(1.0)

    # Calculate scores
    scores_t1 = [0, 0, 0] # Orig, Abliterado, MiMo
    scores_t2 = [0, 0, 0]
    scores_t3 = [0, 0, 0]
    total_eval_t3 = [0, 0, 0]

    for q in master:
        for idx_m, m in enumerate(models):
            if q["tests"]["Test1_T00"][m].get("correct", False):
                scores_t1[idx_m] += 1
            if q["tests"]["Test2_T03"][m].get("correct", False):
                scores_t2[idx_m] += 1
            t3_cell = q["tests"]["Test3_T01"][m]
            if t3_cell.get("status") == "DONE":
                total_eval_t3[idx_m] += 1
                if t3_cell.get("correct", False):
                    scores_t3[idx_m] += 1

    pct_t1 = [(s / 8.0) * 100 for s in scores_t1]
    pct_t2 = [(s / 8.0) * 100 for s in scores_t2]
    pct_t3 = [(scores_t3[i] / total_eval_t3[i]) * 100 if total_eval_t3[i] > 0 else 0 for i in range(3)]

    rects_a1 = ax_acc.bar(x_idx - bar_width, pct_t1, bar_width, label="Test 1: V3 (T=0.0)", color=c_bars[0], edgecolor="#FFFFFF", alpha=0.9)
    rects_a2 = ax_acc.bar(x_idx, pct_t2, bar_width, label="Test 2: Retest (T=0.3)", color=c_bars[1], edgecolor="#FFFFFF", alpha=0.9)
    rects_a3 = ax_acc.bar(x_idx + bar_width, pct_t3, bar_width, label="Test 3: Retest (T=0.1 actual)", color=c_bars[2], edgecolor="#FFFFFF", alpha=0.9)

    ax_acc.set_xticks(x_idx)
    ax_acc.set_xticklabels(model_labels, fontsize=11, fontweight="bold", color="#FFFFFF")
    ax_acc.set_ylabel("Precisión de Aciertos (%)", fontsize=11, fontweight="bold", color="#CAF0F8")
    ax_acc.set_ylim(0, 100)
    ax_acc.set_title("COMPARATIVA DE PRECISIÓN (% DE ACIERTOS)", fontsize=13, fontweight="black", color="#48CAE4", pad=10)
    ax_acc.grid(axis="y", linestyle="--", alpha=0.25, color="#CAF0F8")
    ax_acc.legend(loc="upper left", facecolor="#0B132B", edgecolor="#48CAE4", labelcolor="#FFFFFF", fontsize=9.5)
    ax_acc.tick_params(colors="#CAF0F8")

    # Labels for percentages and count
    for i, rect in enumerate(rects_a1):
        ax_acc.annotate(f"{pct_t1[i]:.1f}%\n({scores_t1[i]}/8)",
                        xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                        fontsize=8.5, fontweight="bold", color="#FFFFFF")
    for i, rect in enumerate(rects_a2):
        ax_acc.annotate(f"{pct_t2[i]:.1f}%\n({scores_t2[i]}/8)",
                        xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                        fontsize=8.5, fontweight="bold", color="#FFFFFF")
    for i, rect in enumerate(rects_a3):
        h = rect.get_height()
        lbl = f"{pct_t3[i]:.1f}%\n({scores_t3[i]}/{total_eval_t3[i]})" if total_eval_t3[i] > 0 else "0.0%\n(⏳)"
        ax_acc.annotate(lbl,
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                        fontsize=8.5, fontweight="bold", color="#FFFFFF")

    # Save Infographic
    OUT_DIR_LAB.mkdir(parents=True, exist_ok=True)
    OUT_DIR_ARTIFACT.mkdir(parents=True, exist_ok=True)
    
    path_lab = OUT_DIR_LAB / "matriz_comparativa_3_tests_gsm8k.png"
    path_art = OUT_DIR_ARTIFACT / "matriz_comparativa_3_tests_gsm8k.png"

    plt.savefig(path_lab, dpi=150, bbox_inches="tight")
    plt.savefig(path_art, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"✅ Infografía generada con éxito:")
    print(f"  - Lab: {path_lab}")
    print(f"  - Artifact: {path_art}")

if __name__ == "__main__":
    data = load_all_data()
    render_infographic(data)
