#!/bin/bash
# ==============================================================================
# Lanzador Exclusivo: Retest de las 8 Preguntas Fallidas de GSM8K
# ==============================================================================
# Evalúa el trío completo (Original, Abliterado V2, Xiaomi MiMo)
# Permite probar diferentes semillas para descartar o confirmar 'mala semilla'
# ==============================================================================

DIR_BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_ENV="/home/genelinux01/IAPower/Herramientas_IA/Cirugia_Tensores/venv/bin/python"

# Semilla por defecto: 2026 (o la que pase el usuario como primer argumento)
SEED=${1:-2026}
# Temperatura por defecto: 0.3 (o la que pase el usuario como segundo argumento)
TEMP=${2:-0.3}

echo "======================================================================"
echo "🎯 LANZANDO RETEST EXCLUSIVO DE LAS 8 PREGUNTAS FALLIDAS"
echo "🎲 Semilla Seleccionada: $SEED"
echo "🌡️ Temperatura: $TEMP"
echo "⚙️ Configuración: Contexto 18k | Salida 16k | KV Cache FP16"
echo "======================================================================"

$PYTHON_ENV "$DIR_BASE/harness_fallidas.py" --seed "$SEED" --temp "$TEMP"

echo ""
echo "======================================================================"
echo "✅ RETEST COMPLETADO"
echo "📂 Reporte comparativo en: $DIR_BASE/resultados/"
echo "📋 Evidencias completas en: $DIR_BASE/evidencia/"
echo "======================================================================"
