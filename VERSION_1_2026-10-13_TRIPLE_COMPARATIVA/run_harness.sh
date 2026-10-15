#!/usr/bin/env bash
# Script lanzador del Harness de Pruebas Qwen 3.5 / Xiaomi MiMo
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VENV="/workspace/IAPower/Herramientas_IA/Cirugia_Tensores/venv/bin/python"

echo "================================================================="
echo "   HARDNESS DE PRUEBAS: QWEN 3.5 9B & XIAOMI MIMO (LAB CANÓNICO)"
echo "================================================================="
echo "1. Ejecutar Sanity Check Rápido (Xiaomi MiMo Q8_0)"
echo "2. Ejecutar Benchmark Triple (Xiaomi vs Original vs Abliterado)"
echo "3. Salir"
echo "================================================================="

read -p "Selecciona una opción [1-3]: " opcion

case "$opcion" in
    1)
        echo "Lanzando Sanity Check..."
        "$PYTHON_VENV" "$SCRIPT_DIR/test_suite_sanity.py" xiaomi_q8
        ;;
    2)
        read -p "Número de preguntas (default 10): " n_preguntas
        n_preguntas="${n_preguntas:-10}"
        echo "Lanzando Benchmark Triple con $n_preguntas preguntas..."
        "$PYTHON_VENV" "$SCRIPT_DIR/harness_runner.py" --models xiaomi_q8 original_q8 abliterado_q8 --dataset gsm8k --samples "$n_preguntas"
        ;;
    3)
        echo "Saliendo."
        exit 0
        ;;
    *)
        echo "Opción no válida."
        exit 1
        ;;
esac
