#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Experimento Paralelo: Xiaomi MiMo con MÁXIMO RAZONAMIENTO (<think> + System Prompt de Verificación)
Siguiendo las recomendaciones oficiales de los creadores en Hugging Face.
Aceleración: 100% GPU NVIDIA GeForce RTX 5080 (16 GB VRAM) vía CUDA (-ngl 99).
"""
import subprocess
import time
import re
import os
import json

LLAMA_CLI = "./llama.cpp/build/bin/llama-cli"
MODEL_PATH = "./models/Qwen3.5-9B/GGUF/Qwen3.5-9B-xiaomi-Q8_0.gguf"
EXP_DIR = "./EXPERIMENTO_MIMO_THINKING_MODIFIED"
os.makedirs(EXP_DIR, exist_ok=True)

QUESTIONS_TO_TEST = [
    {
        "index": 8,
        "question": "Carla is downloading a 200 GB file. Normally she can download 2 GB/minute, but 40% of the way through the download, Windows forces a restart to install updates, which takes 20 minutes. Then Carla has to restart the download from the beginning. How load does it take to download the file?",
        "gold": "160",
        "normal_pred": "100",
        "normal_time_s": 6.78
    },
    {
        "index": 13,
        "question": "Carlos is planting a lemon tree. The tree will cost $90 to plant. Each year it will grow 7 lemons, which he can sell for $1.5 each. It costs $3 a year to water and feed the tree. How many years will it take before he starts earning money on the lemon tree?",
        "gold": "13",
        "normal_pred": "12",
        "normal_time_s": 4.84
    }
]

SYSTEM_PROMPT = "You are an expert mathematical reasoning assistant. Carefully review all given quantities and variables, calculate each step systematically inside <think> tags, and verify all arithmetic operations before outputting your final numerical answer after '#### '."

def extract_answer(text):
    if not text:
        return None
    # 1. Formato #### <valor>
    m = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text)
    if m:
        return m.group(1).replace(',', '').strip()
    # 2. Formato \boxed{...}
    m_box = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', text)
    if m_box:
        return m_box.group(1).replace(',', '').strip()
    # 3. Tras el cierre de </think>
    if "</think>" in text:
        after = text.split("</think>")[-1]
        m_after = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', after)
        if m_after:
            return m_after.group(1).replace(',', '').strip()
        nums = re.findall(r'-?[\d,]+(?:\.\d+)?', after)
        if nums:
            return nums[-1].replace(',', '').strip()
    nums = re.findall(r'-?[\d,]+(?:\.\d+)?', text)
    if nums:
        return nums[-1].replace(',', '').strip()
    return None

def main():
    print("=" * 88, flush=True)
    print("🔬 EXPERIMENTO PARALELO: XIAOMI MIMO CON MÁXIMO RAZONAMIENTO (<think> + SYSTEM PROMPT)", flush=True)
    print("Hardware: 100% GPU NVIDIA GeForce RTX 5080 (16 GB VRAM) vía CUDA", flush=True)
    print("Configuración Oficial: chat_template con enable_thinking y verificación paso a paso", flush=True)
    print("=" * 88 + "\n", flush=True)
    
    results = []
    
    for item in QUESTIONS_TO_TEST:
        idx = item["index"]
        q = item["question"]
        gold = item["gold"]
        
        # Plantilla completa con System Prompt y prefijo <think> activo
        prompt = (
            f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\nQuestion: {q}\nPlease solve step by step, and put your final numerical answer after '#### '.<|im_end|>\n"
            f"<|im_start|>assistant\n<think>\n"
        )
        
        cmd = [
            "taskset", "-c", "0-7",
            LLAMA_CLI,
            "-m", MODEL_PATH,
            "-ngl", "99",
            "-c", "18000",
            "-n", "16000",
            "-b", "512",
            "-ub", "512",
            "--single-turn",
            "--simple-io",
            "--temp", "0.0",
            "-p", prompt
        ]
        
        print(f"--- Evaluando Pregunta #{idx} con MÁXIMO RAZONAMIENTO (Esperado: {gold}) ---", flush=True)
        t0 = time.time()
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
        dt = time.time() - t0
        out = proc.stdout
        pred = extract_answer(out)
        
        correct = False
        try:
            if pred is not None and float(pred) == float(gold):
                correct = True
        except:
            if pred == gold:
                correct = True
                
        icon = "✅" if correct else "❌"
        print(f"  {icon} MiMo (Máximo Razonamiento): Pred={pred} en {dt:.2f}s | Modo Rápido Previo={item['normal_pred']} en {item['normal_time_s']}s", flush=True)
        
        # Guardar traza completa cruda
        log_file = os.path.join(EXP_DIR, f"evidencia_q{idx:03d}_mimo_max_reasoning.log")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"=== Pregunta #{idx} | Gold: {gold} | Pred: {pred} | Tiempo: {dt:.2f}s ===\n")
            f.write(out)
            
        results.append({
            "index": idx,
            "gold": gold,
            "normal_pred": item["normal_pred"],
            "normal_time_s": item["normal_time_s"],
            "thinking_pred": pred,
            "thinking_time_s": round(dt, 2),
            "correct": correct
        })
        print("", flush=True)
        
    rep_path = os.path.join(EXP_DIR, "REPORTE_COMPARATIVO_MIMO_THINKING.md")
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write("# 🔬 Reporte Comparativo: Xiaomi MiMo Modo Normal vs Máximo Razonamiento (<think>)\n\n")
        f.write(f"**Hardware:** NVIDIA GeForce RTX 5080 Laptop (16 GB) | **Precisión KV:** FP16 | **Contexto:** 18,000\n\n")
        f.write("| # | Esperado | MiMo Normal (Sin think) | Tiempo Normal | MiMo Máximo Razonamiento | Tiempo Razonamiento | ¿Corrigió el fallo? |\n")
        f.write("| :-: | :-: | :-: | :-: | :-: | :-: | :-: |\n")
        for r in results:
            fix = "🎉 SÍ, CORREGIDO" if r["correct"] else "❌ No"
            f.write(f"| {r['index']} | `{r['gold']}` | `{r['normal_pred']}` | {r['normal_time_s']}s | `{r['thinking_pred']}` | {r['thinking_time_s']}s | {fix} |\n")
            
    print(f"🏁 Experimento concluido. Reporte generado en: {rep_path}", flush=True)

if __name__ == "__main__":
    main()
