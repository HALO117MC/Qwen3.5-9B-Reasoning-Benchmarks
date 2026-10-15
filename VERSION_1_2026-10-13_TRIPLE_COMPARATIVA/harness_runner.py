#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Runner Modular para Qwen 3.5 9B y Xiaomi MiMo
Permite evaluar cualquier combinación de modelo y benchmark con telemetría completa.
"""
import argparse
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
DATASETS = CONFIG["datasets"]
RESULTS_DIR = os.path.join(BASE_DIR, "resultados")
os.makedirs(RESULTS_DIR, exist_ok=True)

def extract_answer(text, task_type="gsm8k"):
    if not text:
        return None
    if task_type == "hmmt":
        # Extraer \boxed{...}
        match = re.search(r'\\boxed\{([^{}]+)\}', text)
        if match:
            return match.group(1).replace('$', '').replace(',', '').strip()
    # Para gsm8k o fallback
    match = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text)
    if match:
        return match.group(1).replace(',', '').strip()
    match_boxed = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', text)
    if match_boxed:
        return match_boxed.group(1).replace(',', '').strip()
    match2 = re.search(r'(?:is|equals|=)\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
    if match2:
        return match2.group(1).replace(',', '').strip()
    nums = re.findall(r'-?[\d,]+(?:\.\d+)?', text)
    if nums:
        return nums[-1].replace(',', '').strip()
    return None

def query_model(model_path, prompt, timeout=90):
    cmd = [
        "taskset", "-c", "0-7",
        LLAMA_CLI,
        "-m", model_path,
        "-ngl", "99",
        "-c", "4096",
        "-n", "1024",
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
    except Exception as e:
        out = f"Error: {e}"
    dt = time.time() - t0
    return dt, out

def run_harness(model_keys, dataset_key, num_samples):
    dataset_path = DATASETS.get(dataset_key)
    if not dataset_path or not os.path.exists(dataset_path):
        print(f"❌ Error: Dataset '{dataset_key}' no encontrado en {dataset_path}")
        sys.exit(1)
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = [json.loads(line) for line in f][:num_samples]
        
    print("\n" + "="*85)
    print(f"EJECUTANDO TEST HARNESS: {dataset_key.upper()} ({num_samples} preguntas)")
    print(f"Modelos seleccionados: {model_keys}")
    print("="*85 + "\n")
    
    scores = {m: 0 for m in model_keys}
    results = []
    
    for idx, sample in enumerate(samples):
        # Determinar pregunta y respuesta dorada
        if "question" in sample:
            q = sample["question"]
            gold = sample["answer"].split("####")[-1].replace(',', '').strip()
        else:
            q = sample.get("problem", "")
            gold = sample.get("answer", "").replace('$', '').replace(',', '').strip()
            
        prompt = f"<|im_start|>user\n{q}\nPlease reason step by step, and put your final numerical answer after '#### ' or within \\boxed{{}}.<|im_end|>\n<|im_start|>assistant\n"
        
        print(f"[{idx+1:02d}/{num_samples}] Esperado: {gold}")
        row = {"index": idx + 1, "question": q, "gold": gold, "predictions": {}}
        
        for m_key in model_keys:
            m_path = MODELS[m_key]["path"]
            dt, out = query_model(m_path, prompt)
            pred = extract_answer(out, dataset_key)
            
            correct = False
            try:
                if pred is not None and float(pred) == float(gold):
                    correct = True
            except:
                if pred == gold:
                    correct = True
                    
            if correct:
                scores[m_key] += 1
                icon = "✅"
            else:
                icon = "❌"
                
            row["predictions"][m_key] = {"pred": pred, "correct": correct, "time_s": round(dt, 2)}
            print(f"  {icon} {m_key:<15} -> {str(pred):>10} ({dt:.1f}s)")
            
        results.append(row)
        print("", flush=True)
        
    print("="*85)
    print("PUNTUACIÓN HARNESS FINAL:")
    for m_key, sc in scores.items():
        pct = (sc / num_samples) * 100
        print(f" - {MODELS[m_key]['name']:<35}: {sc}/{num_samples} ({pct:.1f}%)")
    print("="*85 + "\n")
    
    # Guardar reporte
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_json = os.path.join(RESULTS_DIR, f"harness_{dataset_key}_{timestamp}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"scores": scores, "total": num_samples, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Resultados guardados en: {out_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Harness para Qwen 3.5 / MiMo")
    parser.add_argument("--models", nargs="+", default=["xiaomi_q8", "original_q8", "abliterado_q8"],
                        help="Modelos a evaluar (claves de config_harness.json o 'all')")
    parser.add_argument("--dataset", default="gsm8k", choices=["gsm8k", "hmmt_feb_2025"],
                        help="Dataset a utilizar")
    parser.add_argument("--samples", type=int, default=10,
                        help="Número de muestras a evaluar")
    args = parser.parse_args()
    
    selected_models = list(MODELS.keys()) if "all" in args.models else args.models
    run_harness(selected_models, args.dataset, args.samples)
