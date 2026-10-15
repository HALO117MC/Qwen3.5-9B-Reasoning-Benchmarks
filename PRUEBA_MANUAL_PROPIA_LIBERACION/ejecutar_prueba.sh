#!/bin/bash
# ==============================================================================
# Lanzador Manual: Test de Liberación y Resistencia al Rechazo (20 Preguntas)
# ==============================================================================
# - Salida Máxima: 16,000 tokens (-n 16000)
# - Ventana de Contexto: 17,000 tokens (-c 17000)
# - KV Cache: Purga total obligatoria entre cada pregunta (contexto = 0)
# - Respuesta Íntegra: Sin recortes ni interrupciones prematuras
# ==============================================================================

DIR_BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_ENV="/workspace/IAPower/Herramientas_IA/Cirugia_Tensores/venv/bin/python"

# Modelo por defecto: Qwen 3.5 9B Abliterado V2 Q8_0
MODELO="./models/Qwen3.5-9B/GGUF/Qwen3.5-9B_ABLITERADO_V2-Q8_0.gguf"

# Si el usuario pasa un argumento por terminal, usa ese modelo
if [ -n "$1" ]; then
    MODELO="$1"
fi

echo "======================================================================"
echo "🚀 INICIANDO TEST DE LIBERACIÓN Y RESISTENCIA AL RECHAZO"
echo "📦 Modelo Seleccionado: $MODELO"
echo "⚙️ Configuración: Salida 16k tokens | Contexto 17k tokens | KV Cache Limpia"
echo "======================================================================"

$PYTHON_ENV "$DIR_BASE/harness_liberacion.py" \
    --model "$MODELO" \
    --max-tokens 16000 \
    --ctx-size 17000 \
    --limit 20

echo ""
echo "======================================================================"
echo "✅ EVALUACIÓN DE LIBERACIÓN COMPLETADA CON ÉXITO"
echo "📂 Reporte listo para DeepSeek: $DIR_BASE/resultados/"
echo "📋 Logs completos guardados en: $DIR_BASE/logs/"
echo "======================================================================"
