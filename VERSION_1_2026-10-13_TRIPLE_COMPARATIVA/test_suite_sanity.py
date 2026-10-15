#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sanity Test Suite para Qwen 3.5 9B & Xiaomi MiMo
Verifica:
1. Carga del modelo en VRAM (NVIDIA RTX 5080)
2. Inferencia y velocidad (tokens/segundo)
3. Cumplimiento de ChatML y salida sin corrupción de tensores
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

def run_sanity_test(model_key="xiaomi_q8"):
    if model_key not in MODELS:
        print(f"Error: Modelo '{model_key}' no encontrado. Opciones: {list(MODELS.keys())}")
        sys.exit(1)
        
    m_info = MODELS[model_key]
    model_path = m_info["path"]
    model_name = m_info["name"]
    
    print("\n" + "="*80)
    print(f"SANITY CHECK: {model_name}")
    print(f"Ruta: {model_path}")
    print(f"GPU: {CONFIG['hardware']['gpu']}")
    print("="*80 + "\n")
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Archivo de modelo no existe: {model_path}")
        return False
        
    prompt = "<|im_start|>user\nResponde en exactamente dos oraciones: ¿Qué es la inteligencia artificial y cuál es su objetivo?<|im_end|>\n<|im_start|>assistant\n"
    
    cmd = [
        "taskset", "-c", "0-7",
        LLAMA_CLI,
        "-m", model_path,
        "-ngl", "99",
        "-c", "2048",
        "-n", "128",
        "-b", "19",
        "-ub", "19",
        "-ctk", "q4_0",
        "-ctv", "q4_0",
        "--temp", "0.2",
        "--single-turn",
        "--simple-io",
        "--no-warmup",
        "-p", prompt
    ]
    
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
        dt = time.time() - t0
        output = proc.stdout
    except Exception as e:
        print(f"❌ Error al ejecutar llama-cli: {e}")
        return False
        
    # Extraer velocidad y respuesta
    tps_match = re.search(r'Generation:\s*([\d\.]+)\s*t/s', output)
    tps = tps_match.group(1) if tps_match else "N/A"
    
    # Extraer respuesta limpia
    resp = output.split("<|im_start|>assistant")[-1].strip()
    resp = resp.replace("[Start thinking]", "").split("[ Prompt:")[0].strip()
    
    passed = proc.returncode == 0 and len(resp) > 10 and "error" not in output.lower()
    
    print("--- RESULTADO DE LA PRUEBA ---")
    print(f"Estado       : {'✅ EXITOSO (PASS)' if passed else '❌ FALLO (FAIL)'}")
    print(f"Tiempo Total : {dt:.2f} s")
    print(f"Velocidad    : {tps} tokens/s")
    print(f"Respuesta:\n{resp}\n")
    print("="*80 + "\n")
    return passed

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "xiaomi_q8"
    run_sanity_test(target)
