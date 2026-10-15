#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Runner V3: Evaluación Oficial GSM8K (100 Preguntas) - Trío Qwen 3.5 9B
Modelos:
1. Qwen 3.5 9B Original (Q8_0)
2. Qwen 3.5 9B Abliterado V2 (Q8_0)
3. Xiaomi MiMo-V2.6-Distill-Qwen-9B (Q8_0)

Parámetros V3:
- Context Window (-c): 18,000 tokens
- Max Output Tokens (-n): 16,000 tokens (Anti-truncamiento total para cadenas de sobrepensamiento profundo)
- Precisión KV Cache: FP16 puro (100% fidelidad matemática en atención, sin ruido de cuantización Q4)
- Aceleración: 100% GPU NVIDIA GeForce RTX 5080 (16 GB VRAM) vía CUDA (-ngl 99)
- Aislamiento de Contexto: 100% AISLADO (proceso nuevo por pregunta y modelo, 0 acumulación de contexto)
- Registro de Evidencias: Guarda la salida cruda completa de cada pregunta y modelo en evidencia/
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
EVIDENCE_DIR = os.path.join(SCRIPT_DIR, "evidencia")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

REPORT_MD = os.path.join(RESULTS_DIR, "reporte_100_gsm8k_trio.md")
RESULT_JSON = os.path.join(RESULTS_DIR, "resultados_100_gsm8k_trio.json")

MODELS = {
    "Original": "./models/Qwen3.5-9B/GGUF/Qwen3.5-9B-original-Q8_0.gguf",
    "Abliterado_V2": "./models/Qwen3.5-9B/GGUF/Qwen3.5-9B_ABLITERADO_V2-Q8_0.gguf",
    "Xiaomi_MiMo": "./models/Qwen3.5-9B/GGUF/Qwen3.5-9B-xiaomi-Q8_0.gguf"
}

LLAMA_CLI = "./llama.cpp/build/bin/llama-cli"

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
    # 3. Formato tras cierre de </think>
    if "</think>" in text:
        after_think = text.split("</think>")[-1]
        m_after = re.search(r'####\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', after_think)
        if m_after:
            return m_after.group(1).replace(',', '').strip()
        m_box = re.search(r'\\boxed\{(-?[\d,]+(?:\.\d+)?)\}', after_think)
        if m_box:
            return m_box.group(1).replace(',', '').strip()
        m_eq = re.search(r'(?:is|equals|=|es|total)\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', after_think, re.IGNORECASE)
        if m_eq:
            return m_eq.group(1).replace(',', '').strip()
        nums_after = re.findall(r'-?[\d,]+(?:\.\d+)?', after_think)
        if nums_after:
            return nums_after[-1].replace(',', '').strip()
    # 4. Igualdades o asignaciones generales
    match2 = re.search(r'(?:is|equals|=)\s*\$?\s*(-?[\d,]+(?:\.\d+)?)', text, re.IGNORECASE)
    if match2:
        return match2.group(1).replace(',', '').strip()
    # 5. Último número en el texto completo
    nums = re.findall(r'-?[\d,]+(?:\.\d+)?', text)
    if nums:
        return nums[-1].replace(',', '').strip()
    return None

def query_model(model_path, prompt, q_idx, model_name, timeout=600):
    """
    Cada invocación ejecuta un proceso de llama-cli totalmente nuevo y confinado a P-cores.
    Garantía de contexto = 0 entre preguntas.
    Salida completa persistida en evidencia/ para auditoría exacta.
    """
    cmd = [
        "taskset", "-c", "0-7",
        LLAMA_CLI,
        "-m", model_path,
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
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        out = proc.stdout
    except Exception as e:
        out = f"Error: {e}"
    dt = time.time() - t0
    
    # Guardar evidencia completa cruda
    evid_path = os.path.join(EVIDENCE_DIR, f"q{q_idx:03d}_{model_name}.log")
    try:
        with open(evid_path, "w", encoding="utf-8") as fe:
            fe.write(f"=== Modelo: {model_name} | Pregunta: {q_idx} | Tiempo: {dt:.2f}s ===\n")
            fe.write(out)
    except Exception:
        pass
        
    ans = extract_answer(out)
    return ans, dt, out

def save_progress(scores, total_done, total_samples, detailed_results):
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump({"scores": scores, "total_done": total_done, "total_samples": total_samples, "details": detailed_results}, f, indent=2, ensure_ascii=False)
        
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("# 📊 Reporte Oficial GSM8K (100 Preguntas) - Trío Qwen 3.5 9B [Versión 3]\n\n")
        f.write(f"**Progreso:** {total_done}/{total_samples} preguntas evaluadas | **Cuantización:** GGUF Q8_0 | **VRAM:** 100% RTX 5080 (16 GB)\n")
        f.write(f"**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16 puro (sin pérdida de precisión)\n\n")
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
        
    print("=" * 88, flush=True)
    print("BENCHMARK OFICIAL GSM8K (100 PREGUNTAS): TRIO QWEN 3.5 9B [VERSION 3]", flush=True)
    print(f"Dataset Oficial: {DATASET_FILE} ({len(samples)} preguntas)", flush=True)
    print("Política de Contexto: 100% AISLADO (0 tokens acumulados entre preguntas)", flush=True)
    print("Parámetros: Contexto 18,000 tokens | Salida máx 16,000 tokens | KV Cache: FP16 puro en GPU", flush=True)
    print("Aceleración: 100% NVIDIA RTX 5080 (16 GB VRAM) vía CUDA", flush=True)
    print("=" * 88 + "\n", flush=True)
    
    scores = {m: 0 for m in MODELS}
    detailed_results = []
    
    if os.path.exists(RESULT_JSON):
        try:
            with open(RESULT_JSON, "r", encoding="utf-8") as fj:
                data_prev = json.load(fj)
                scores = data_prev.get("scores", scores)
                detailed_results = data_prev.get("details", [])
                print(f"🔄 Reanudando ejecución desde la pregunta {len(detailed_results) + 1} ({len(detailed_results)} ya completadas y resguardadas)...", flush=True)
        except Exception as e:
            print(f"Aviso al cargar estado previo: {e}", flush=True)
    
    for idx, s in enumerate(samples):
        if idx < len(detailed_results):
            continue
        q = s["question"]
        gold = s["answer"].split("####")[-1].replace(',', '').strip()
        prompt = f"<|im_start|>user\nQuestion: {q}\nPlease solve step by step, and put your final numerical answer after '#### '.<|im_end|>\n<|im_start|>assistant\n"
        
        row_res = {"index": idx + 1, "question": q, "gold": gold, "models": {}}
        print(f"--- Pregunta [{idx+1:03d}/{num_samples}] (Esperado: {gold}) ---", flush=True)
        
        for name, path in MODELS.items():
            if name == "Xiaomi_MiMo":
                # Xiaomi MiMo con MÁXIMO RAZONAMIENTO oficial (<think> + System Prompt de verificación)
                model_prompt = (
                    f"<|im_start|>system\nYou are an expert mathematical reasoning assistant. Carefully review all given quantities and variables, calculate each step systematically inside <think> tags, and verify all arithmetic operations before outputting your final numerical answer after '#### '.<|im_end|>\n"
                    f"<|im_start|>user\nQuestion: {q}\nPlease solve step by step, and put your final numerical answer after '#### '.<|im_end|>\n"
                    f"<|im_start|>assistant\n<think>\n"
                )
            else:
                model_prompt = prompt
            ans, dt, out = query_model(path, model_prompt, idx + 1, name)
            correct = False
            try:
                if ans is not None and float(ans) == float(gold):
                    correct = True
            except Exception:
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
        
    print("=" * 88, flush=True)
    print("🏁 EVALUACIÓN VERSION 3 COMPLETADA CON ÉXITO", flush=True)
    for name, sc in scores.items():
        print(f"  - {name}: {sc}/{num_samples} ({sc/num_samples*100:.1f}%)", flush=True)
    print("=" * 88, flush=True)

if __name__ == "__main__":
    n = 100
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    run_evaluation(n)
