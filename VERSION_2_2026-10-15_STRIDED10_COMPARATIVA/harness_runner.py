#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Runner V2.1 - 18k Contexto / 16k Salida / Prefijo <think> Activado
Triple Comparativa: Original Q8, Abliterado V2 Q8 y Xiaomi MiMo Q8
"""
import subprocess
import json
import re
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config_harness.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

LLAMA_CLI = CONFIG["llama_binaries"]["llama_cli"]
MODELS = CONFIG["models"]
DATASET_FILE = CONFIG["datasets"]["strided_10"]
RESULTS_DIR = os.path.join(BASE_DIR, "resultados")
EVIDENCIA_DIR = os.path.join(BASE_DIR, "evidencia")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(EVIDENCIA_DIR, exist_ok=True)

def extract_answer(text):
    if not text:
        return None
    # 1. Buscar formato oficial #### <numero>
    match = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text)
    if match:
        return match.group(1).replace(',', '').strip()
    # 2. Buscar \boxed{<numero>}
    match_boxed = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', text)
    if match_boxed:
        return match_boxed.group(1).replace(',', '').strip()
    # 3. Buscar si concluye después de </think> con una frase clara
    if "</think>" in text:
        post_think = text.split("</think>")[-1]
        m_post = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', post_think)
        if m_post:
            return m_post.group(1).replace(',', '').strip()
        nums = re.findall(r'-?[\d,]+(?:\.\d+)?', post_think)
        if nums:
            return nums[-1].replace(',', '').strip()
    # 4. Fallback estándar
    match2 = re.search(r'(?:is|equals|=|es igual a|total of)\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
    if match2:
        return match2.group(1).replace(',', '').strip()
    nums = re.findall(r'-?[\d,]+(?:\.\d+)?', text)
    if nums:
        return nums[-1].replace(',', '').strip()
    return None

def query_model(model_path, prompt, timeout=300):
    cmd = [
        "taskset", "-c", "0-7",
        LLAMA_CLI,
        "-m", model_path,
        "-ngl", "99",
        "-c", "18000",
        "-n", "16384",
        "-b", "19",
        "-ub", "19",
        "-ctk", "q4_0",
        "-ctv", "q4_0",
        "--single-turn",
        "--simple-io",
        "--temp", "0.0",
        "-p", prompt
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        out = proc.stdout
        dur = time.time() - t0
        return out, dur
    except subprocess.TimeoutExpired:
        return "TIMEOUT", timeout
    except Exception as e:
        return f"ERROR: {e}", 0.0

def main():
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f if line.strip()]

    print(f"=== INICIANDO HARNESS V2.1: 18K CTX / 16K SALIDA / PREFIJO <think> ===")
    print("Modelos a evaluar:")
    for k, m in MODELS.items():
        print(f" - [{k}]: {m['name']}")

    results = {k: {"correct": 0, "total": len(tasks), "details": []} for k in MODELS}

    for i, t in enumerate(tasks):
        orig_idx = t.get("original_index", i + 1)
        q = t["question"]
        expected_raw = t["answer"]
        expected = expected_raw.split("####")[-1].strip()

        print(f"\n--- Tarea [{orig_idx:02d}] (Esperado: {expected}) ---")
        # Inyectar <think> explícito para activar el modo de razonamiento profundo
        prompt = (
            "<|im_start|>system\n"
            "You are an expert analytical and mathematical reasoning assistant. "
            "Carefully review all given premises and variables, compute each step systematically "
            "inside <think> and </think> tags, and finish your answer with #### <result>.<|im_end|>\n"
            f"<|im_start|>user\n{q}<|im_end|>\n"
            "<|im_start|>assistant\n<think>\n"
        )

        for k, m in MODELS.items():
            out, dur = query_model(m["path"], prompt)
            pred = extract_answer(out)
            is_correct = (pred == expected)
            if is_correct:
                results[k]["correct"] += 1
                status_icon = "✅"
            else:
                status_icon = "❌"

            results[k]["details"].append({
                "index": orig_idx,
                "expected": expected,
                "pred": pred,
                "correct": is_correct,
                "duration_s": round(dur, 2)
            })

            # Guardar evidencia
            evid_file = os.path.join(EVIDENCIA_DIR, f"tarea_{orig_idx:02d}_{k}.txt")
            with open(evid_file, "w", encoding="utf-8") as ef:
                ef.write(f"PROMPT:\n{prompt}\n\nOUTPUT:\n{out}")

            print(f"  {status_icon} {k:15s} -> Pred: {str(pred):>10s} ({dur:.1f}s)")

    # Resumen y Reporte Markdown
    md_report = os.path.join(RESULTS_DIR, "reporte_strided_10_comparativo_16k.md")
    with open(md_report, "w", encoding="utf-8") as f:
        f.write("# 📊 Reporte Comparativo Triple V2.1: 18k Contexto / 16k Salida / <think> Tag\n\n")
        f.write(f"**Fecha:** {time.strftime('%Y-%m-%d %H:%M:%S')} | **Parámetros:** `-c 18000 -n 16384` | **Prefijo:** `<think>`\n\n")
        f.write("### 🏆 Puntuaciones Finales\n\n")
        f.write("| Modelo | Aciertos | Precisión | Tiempo Promedio |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for k, res in results.items():
            acc = (res["correct"] / res["total"]) * 100
            avg_t = sum(d["duration_s"] for d in res["details"]) / len(res["details"])
            f.write(f"| **{MODELS[k]['name']}** | {res['correct']}/{res['total']} | **{acc:.1f}%** | {avg_t:.2f} s |\n")

        f.write("\n---\n\n### 📝 Desglose Tarea por Tarea\n\n")
        f.write("| # Original | Esperado | Original Q8 | Abliterado V2 Q8 | Xiaomi MiMo Q8 |\n")
        f.write("| :-: | :-: | :-: | :-: | :-: |\n")

        for idx_row in range(len(tasks)):
            row_idx = tasks[idx_row].get("original_index", idx_row + 1)
            exp = tasks[idx_row]["answer"].split("####")[-1].strip()
            orig_p = results["original_q8"]["details"][idx_row]
            ablit_p = results["abliterado_q8"]["details"][idx_row]
            mimo_p = results["xiaomi_q8"]["details"][idx_row]

            icon_orig = "✅" if orig_p["correct"] else "❌"
            icon_ablit = "✅" if ablit_p["correct"] else "❌"
            icon_mimo = "✅" if mimo_p["correct"] else "❌"

            f.write(f"| `{row_idx}` | `{exp}` | {icon_orig} `{orig_p['pred']}` ({orig_p['duration_s']}s) | {icon_ablit} `{ablit_p['pred']}` ({ablit_p['duration_s']}s) | {icon_mimo} `{mimo_p['pred']}` ({mimo_p['duration_s']}s) |\n")

    print("\n" + "="*70)
    print("RESULTADOS FINALES V2.1:")
    for k, res in results.items():
        acc = (res["correct"] / res["total"]) * 100
        print(f" - {MODELS[k]['name']}: {res['correct']}/{res['total']} ({acc:.1f}%)")
    print(f"Reporte generado en: {md_report}")
    print("="*70)

if __name__ == "__main__":
    main()
