#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Runner V2: Evaluación Completa 100 Preguntas GSM8K (Hugging Face)
Modelos:
- Qwen 3.5 9B Original
- Qwen 3.5 9B Abliterado V2
- Xiaomi MiMo-V2.6-Distill-Qwen-9B

Mejoras V2:
1. Token budget expandido a -n 2048 para evitar agotamiento de tokens por sobrepensamiento.
2. Aislamiento absoluto de proceso por pregunta (cero fuga de contexto, memoria limpia en cada iteración).
3. Guardado en caliente (flush inmediato) tras cada pregunta en JSON y Markdown.
"""
import subprocess
import json
import re
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(SCRIPT_DIR, "datasets", "gsm8k_test_hf.jsonl")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "resultados")
os.makedirs(RESULTS_DIR, exist_ok=True)

REPORT_MD = os.path.join(RESULTS_DIR, "reporte_100_gsm8k_trio.md")
RESULT_JSON = os.path.join(RESULTS_DIR, "resultados_100_gsm8k_trio.json")

MODELS = {
    "Original": "/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/Boveda_llm/Qwen3.5-9B/GGUF/Qwen3.5-9B-original-Q8_0.gguf",
    "Abliterado_V2": "/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/Boveda_llm/Qwen3.5-9B/GGUF/Qwen3.5-9B_ABLITERADO_V2-Q8_0.gguf",
    "Xiaomi_MiMo": "/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/Boveda_llm/Qwen3.5-9B/GGUF/Qwen3.5-9B-xiaomi-Q8_0.gguf"
}

LLAMA_CLI = "/home/genelinux01/IAPower/Herramientas_IA/llama.cpp/build/bin/llama-cli"

def extract_answer(text):
    if not text:
        return None
    # 1. Formato oficial #### <valor>
    match = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text)
    if match:
        return match.group(1).replace(',', '').strip()
    # 2. Formato \boxed{...}
    match_boxed = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', text)
    if match_boxed:
        return match_boxed.group(1).replace(',', '').strip()
    # 3. Igualdades o asignaciones
    match2 = re.search(r'(?:is|equals|=)\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
    if match2:
        return match2.group(1).replace(',', '').strip()
    # 4. Último número fuera del bloque think si existe
    if "</think>" in text:
        after_think = text.split("</think>")[-1]
        nums_after = re.findall(r'-?[\d,]+(?:\.\d+)?', after_think)
        if nums_after:
            return nums_after[-1].replace(',', '').strip()
    nums = re.findall(r'-?[\d,]+(?:\.\d+)?', text)
    if nums:
        return nums[-1].replace(',', '').strip()
    return None

def query_model(model_path, prompt, timeout=240):
    """
    Cada invocación ejecuta un proceso de llama-cli totalmente nuevo y confinado a P-cores.
    Al finalizar el proceso, Linux libera la VRAM y RAM; la siguiente pregunta inicia con contexto = 0.
    """
    cmd = [
        "taskset", "-c", "0-7",
        LLAMA_CLI,
        "-m", model_path,
        "-ngl", "99",
        "-c", "16384",
        "-n", "8192",
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
    ans = extract_answer(out)
    return ans, dt, out

def save_progress(scores, total_done, total_samples, detailed_results):
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump({"scores": scores, "total_done": total_done, "total_samples": total_samples, "details": detailed_results}, f, indent=2, ensure_ascii=False)
        
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("# 📊 Reporte Oficial GSM8K (100 Preguntas) - Trio Qwen 3.5 9B\n\n")
        f.write(f"**Progreso:** {total_done}/{total_samples} preguntas evaluadas | **Cuantización:** GGUF Q8_0 | **VRAM:** 100% RTX 5080\n\n")
        f.write("### 🏆 Puntuaciones Parciales / Finales\n\n")
        f.write("| Modelo | Aciertos | Precisión | Estado |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for name, sc in scores.items():
            pct = (sc / total_done) * 100 if total_done > 0 else 0
            f.write(f"| **{name}** | {sc}/{total_done} | **{pct:.1f}%** | {'🟢 En progreso' if total_done < total_samples else '🏁 Finalizado'} |\n")
        f.write("\n---\n\n### 📝 Desglose de Preguntas\n\n")
        f.write("| # | Esperado | Original | Abliterado V2 | Xiaomi MiMo |\n")
        f.write("| :-: | :---: | :---: | :---: | :---: |\n")
        for r in detailed_results:
            o_m = r["models"]["Original"]
            a_m = r["models"]["Abliterado_V2"]
            x_m = r["models"]["Xiaomi_MiMo"]
            f.write(f"| {r['index']} | `{r['gold']}` | {'✅' if o_m['correct'] else '❌'} `{o_m['pred']}` ({o_m['time_s']}s) | {'✅' if a_m['correct'] else '❌'} `{a_m['pred']}` ({a_m['time_s']}s) | {'✅' if x_m['correct'] else '❌'} `{x_m['pred']}` ({x_m['time_s']}s) |\n")

def run_evaluation(num_samples=100):
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        samples = [json.loads(line) for line in f][:num_samples]
        
    print("=" * 85, flush=True)
    print(f"BENCHMARK COMPLETO GSM8K (100 PREGUNTAS): TRIO QWEN 3.5 9B", flush=True)
    print(f"Dataset Oficial: {DATASET_FILE} ({len(samples)} preguntas)", flush=True)
    print(f"Política de Contexto: 100% AISLADO (0 tokens acumulados entre preguntas)", flush=True)
    print(f"Token Budget: -n 2048 (Anti-Loop Exhaustion)", flush=True)
    print("=" * 85 + "\n", flush=True)
    
    scores = {m: 0 for m in MODELS}
    detailed_results = []
    
    for idx, s in enumerate(samples):
        q = s["question"]
        gold = s["answer"].split("####")[-1].replace(',', '').strip()
        prompt = f"<|im_start|>user\nQuestion: {q}\nPlease solve step by step, and put your final numerical answer after '#### '.<|im_end|>\n<|im_start|>assistant\n"
        
        row_res = {"index": idx + 1, "question": q, "gold": gold, "models": {}}
        print(f"--- Pregunta [{idx+1:03d}/{num_samples}] (Esperado: {gold}) ---", flush=True)
        
        for name, path in MODELS.items():
            ans, dt, out = query_model(path, prompt)
            correct = False
            try:
                if ans is not None and float(ans) == float(gold):
                    correct = True
            except:
                if ans == gold:
                    correct = True
            if correct:
                scores[name] += 1
                icon = "✅"
            else:
                icon = "❌"
            row_res["models"][name] = {"pred": ans, "correct": correct, "time_s": round(dt, 2)}
            print(f"  {icon} {name:<14} -> Pred: {str(ans):>8} ({dt:.1f}s)", flush=True)
            
        detailed_results.append(row_res)
        save_progress(scores, idx + 1, num_samples, detailed_results)
        print("", flush=True)
        
    print("=" * 85, flush=True)
    print("BENCHMARK COMPLETO FINALIZADO (100/100 PREGUNTAS):", flush=True)
    for name, sc in scores.items():
        pct = (sc / num_samples) * 100
        print(f" - {name:<14}: {sc}/{num_samples} ({pct:.1f}%)", flush=True)
    print("=" * 85, flush=True)

if __name__ == "__main__":
    n = 100
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    run_evaluation(n)
