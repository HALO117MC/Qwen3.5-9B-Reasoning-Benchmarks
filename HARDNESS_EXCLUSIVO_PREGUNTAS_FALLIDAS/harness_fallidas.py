#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Exclusivo para Preguntas Fallidas de GSM8K (Trío Qwen 3.5 9B)
===================================================================
- Evalúa exclusivamente las 8 preguntas donde al menos un modelo falló en la corrida de 100.
- Soporta configuración de Semilla (--seed) y Temperatura (--temp) para verificar si el
  error original se debió a una 'mala semilla' estocástica.
- Aislamiento estricto de contexto: contexto = 0 por pregunta (purga total de VRAM).
- Parámetros: Contexto 18,000 tokens (-c 18000), Salida 16,000 tokens (-n 16000), FP16.
- Genera reporte comparativo directo: Corrida 1 (V3) vs Corrida 2 (Retest Semilla).
"""

import os
import re
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset_8_fallidas_gsm8k.json"
EVIDENCE_DIR = BASE_DIR / "evidencia"
RESULTS_DIR = BASE_DIR / "resultados"

MODELS = {
    "Original": "/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/Boveda_llm/Qwen3.5-9B/GGUF/Qwen3.5-9B-original-Q8_0.gguf",
    "Abliterado_V2": "/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/Boveda_llm/Qwen3.5-9B/GGUF/Qwen3.5-9B_ABLITERADO_V2-Q8_0.gguf",
    "Xiaomi_MiMo": "/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/Boveda_llm/Qwen3.5-9B/GGUF/Qwen3.5-9B-xiaomi-Q8_0.gguf"
}

LLAMA_CLI = "/home/genelinux01/IAPower/Herramientas_IA/llama.cpp/build/bin/llama-cli"

def clean_output(raw_text):
    text = re.sub(r'\[\s*Prompt:.*?\]', '', raw_text, flags=re.DOTALL)
    if '<|im_start|>assistant' in text:
        text = text.split('<|im_start|>assistant', 1)[1]
    return text.strip()

def extract_answer(raw_text):
    if not raw_text:
        return None
    text = clean_output(raw_text)
    
    # Strip thinking blocks to avoid false matches inside internal reasoning
    if "[End thinking]" in text:
        text = text.split("[End thinking]", 1)[1]
    elif "</think>" in text:
        text = text.split("</think>", 1)[1]
    text = text.strip()
    
    # 1. #### valor
    match = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text)
    if match:
        return match.group(1).replace(',', '').strip()
    # 2. \boxed{valor}
    match_boxed = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', text)
    if match_boxed:
        return match_boxed.group(1).replace(',', '').strip()
    # 3. Explicit Answer: or **Answer:** lines
    ans_lines = [l.strip() for l in text.splitlines() if re.search(r'(?:\*\*Answer:?|Answer:)', l, re.IGNORECASE)]
    if ans_lines:
        line = ans_lines[-1]
        bold = re.findall(r'\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)\s*\*\*', line)
        if bold:
            return bold[-1].replace(',', '').strip()
        nums = re.findall(r'\$?(-?[\d,]+(?:\.\d+)?)', line)
        if nums:
            return nums[-1].replace(',', '').strip()
    # 4. Bold numbers in response
    bold_all = re.findall(r'\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)\s*\*\*', text)
    if bold_all:
        return bold_all[-1].replace(',', '').strip()
    # 5. Fallback: Último número de la respuesta
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

def query_model(model_name, model_path, prompt, q_idx, seed=2026, temp=0.3, max_tokens=16000, ctx_size=18000):
    # Formateo estricto oficial de GSM8K
    if model_name == "Xiaomi_MiMo":
        formatted_prompt = (
            f"<|im_start|>system\nYou are an expert mathematical reasoning assistant. Carefully review all given quantities and variables, calculate each step systematically inside <think> tags, and verify all arithmetic operations before outputting your final numerical answer after '#### '.<|im_end|>\n"
            f"<|im_start|>user\nQuestion: {prompt}\nPlease solve step by step, and put your final numerical answer after '#### '.<|im_end|>\n"
            f"<|im_start|>assistant\n<think>\n"
        )
    else:
        formatted_prompt = (
            f"<|im_start|>user\nQuestion: {prompt}\nPlease solve step by step, and put your final numerical answer after '#### '.<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

    cmd = [
        "taskset", "-c", "0-7",
        LLAMA_CLI,
        "-m", model_path,
        "-p", formatted_prompt,
        "-n", str(max_tokens),
        "-c", str(ctx_size),
        "-ngl", "99",
        "-b", "512",
        "-ub", "512",
        "--single-turn",
        "--temp", str(temp),
        "--seed", str(seed),
        "--simple-io",
        "--no-display-prompt"
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", timeout=600)
        out = proc.stdout
    except Exception as e:
        out = f"Error: {e}"
    dt = time.time() - t0

    # Guardar log de evidencia
    evid_path = EVIDENCE_DIR / f"retest_q{q_idx:03d}_{model_name}_seed{seed}_temp{temp}.log"
    with open(evid_path, "w", encoding="utf-8") as fe:
        fe.write(f"=== Retest Q{q_idx} | Modelo: {model_name} | Seed: {seed} | Temp: {temp} | Tiempo: {dt:.2f}s ===\n")
        fe.write(out)

    ans = extract_answer(out)
    time.sleep(1.0) # Purga de VRAM
    return ans, dt, out

def main():
    parser = argparse.ArgumentParser(description="Harness de Retest para Preguntas Fallidas")
    parser.add_argument("--seed", type=int, default=2026, help="Semilla pseudoaleatoria para evaluar estocasticidad")
    parser.add_argument("--temp", type=float, default=0.3, help="Temperatura de muestreo (default: 0.3)")
    args = parser.parse_args()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print("=" * 80)
    print(f"🔬 INICIANDO RETEST DE PREGUNTAS FALLIDAS (TOTAL: {len(questions)} PREGUNTAS)")
    print(f"🎲 Semilla Configurada: {args.seed} | Temperatura: {args.temp}")
    print(f"📦 Modelos: Original, Abliterado_V2, Xiaomi_MiMo (Q8_0)")
    print(f"⚙️ Configuración: Contexto -c 18000 | Salida -n 16000 | FP16 KV Cache")
    print(f"🔒 Aislamiento: Contexto = 0 estricto entre cada inferencia")
    print("=" * 80)

    retest_results = []
    scores = {m: 0 for m in MODELS}

    for item in questions:
        q_idx = item["index"]
        q_text = item["question"]
        gold = item["gold"]
        prior = item.get("prior_run_v3", {})

        print(f"\n" + "─" * 60)
        print(f"▶ PREGUNTA #{q_idx} (Valor Esperado Gold: {gold})")
        print(f"  Enunciado: {q_text[:90]}...")
        print("─" * 60)

        q_entry = {
            "index": q_idx,
            "gold": gold,
            "question": q_text,
            "prior_run_v3": prior,
            "retest": {}
        }

        for model_name, model_path in MODELS.items():
            print(f"  ⏳ Evaluando [{model_name}]...", end="", flush=True)
            pred, dt, _ = query_model(model_name, model_path, q_text, q_idx, seed=args.seed, temp=args.temp)
            correct = compare_numbers(pred, gold)
            if correct:
                scores[model_name] += 1

            status_icon = "✅" if correct else "❌"
            prior_correct = prior.get(model_name, {}).get("correct", False)
            prior_pred = prior.get(model_name, {}).get("pred", "N/A")
            
            # Evaluar si cambió con la semilla
            cambio_str = ""
            if not prior_correct and correct:
                cambio_str = " (🎉 ¡SE CORRIGIÓ CON LA NUEVA SEMILLA!)"
            elif prior_correct and not correct:
                cambio_str = " (⚠️ Regresión frente a corrida anterior)"
            elif not prior_correct and not correct:
                cambio_str = " (Persiste fallo sistemático)"
            else:
                cambio_str = " (Mantuvo acierto)"

            print(f" -> {status_icon} Pred: {pred} ({dt:.2f}s){cambio_str}")

            q_entry["retest"][model_name] = {
                "pred": pred,
                "correct": correct,
                "time_s": dt,
                "prior_pred": prior_pred,
                "prior_correct": prior_correct
            }

        retest_results.append(q_entry)

    # Guardar JSON con resultados completos
    json_path = RESULTS_DIR / f"resultado_retest_seed_{args.seed}_temp_{args.temp}.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump({
            "seed": args.seed,
            "temperature": args.temp,
            "total_questions": len(questions),
            "scores": scores,
            "details": retest_results
        }, jf, indent=2, ensure_ascii=False)

    # Generar Reporte Markdown Comparativo
    md_path = RESULTS_DIR / f"reporte_comparativo_retest_seed_{args.seed}_temp_{args.temp}.md"
    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write(f"# 📊 REPORTE DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)\n\n")
        mf.write(f"**Semilla Evaluada:** `{args.seed}` | **Temperatura:** `{args.temp}`\n")
        mf.write(f"**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16\n\n")
        mf.write(f"### 🏆 Puntuaciones en el Retest ({len(questions)} Preguntas Clave)\n\n")
        mf.write(f"| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |\n")
        mf.write(f"| :--- | :---: | :---: | :---: |\n")
        for m in MODELS:
            sc = scores[m]
            pct = (sc / len(questions)) * 100
            mf.write(f"| **{m}** | **{sc} / {len(questions)}** | **{pct:.1f}%** | 96.0% (96/100) |\n")
        
        mf.write(f"\n---\n\n### 🔍 Comparativa Detallada Pregunta por Pregunta\n\n")
        mf.write(f"| # | Esperado | Original (Prev -> Retest) | Abliterado V2 (Prev -> Retest) | Xiaomi MiMo (Prev -> Retest) |\n")
        mf.write(f"| :-: | :---: | :---: | :---: | :---: |\n")

        for r in retest_results:
            idx = r["index"]
            gold = r["gold"]
            
            def fmt(m):
                d = r["retest"][m]
                p_old = d["prior_pred"]
                p_new = d["pred"]
                c_new = d["correct"]
                icon = "✅" if c_new else "❌"
                return f"{icon} `{p_old}` ➔ `{p_new}` ({d['time_s']:.1f}s)"

            mf.write(f"| {idx} | `{gold}` | {fmt('Original')} | {fmt('Abliterado_V2')} | {fmt('Xiaomi_MiMo')} |\n")

        mf.write(f"\n---\n\n### 📝 Notas y Diagnóstico de Semilla\n")
        mf.write(f"- Si una pregunta pasó de ❌ a ✅, confirma que el error previo fue estocástico (mala semilla).\n")
        mf.write(f"- Si persiste en ❌ con el mismo número, confirma una limitación epistémica o ambigüedad intrínseca en el problema.\n")

    print("\n" + "=" * 80)
    print(f"🏁 RETEST CONCLUIDO CON ÉXITO:")
    for m in MODELS:
        print(f"  {m:14s}: {scores[m]} / {len(questions)} aciertos ({(scores[m]/len(questions))*100:.1f}%)")
    print(f"  📄 JSON Resultados: {json_path}")
    print(f"  📋 Reporte Markdown Comparativo: {md_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
