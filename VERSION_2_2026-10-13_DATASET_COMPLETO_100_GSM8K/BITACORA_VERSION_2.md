# 📋 Bitácora Técnica de Versión: V2 (2026-10-13)

**Identificador de Versión:** `VERSION_2_2026-10-13_DATASET_COMPLETO_100_GSM8K`  
**Ubicación:** `./VERSION_2_2026-10-13_DATASET_COMPLETO_100_GSM8K/`  
**Fecha:** 13 de Octubre de 2026  
**Entorno de Ejecución:** LAB Canónico (`HARDNES-PRUEBAS/HARDEN-PRUEBA-QWEN3-5-9B`)  

---

## 🚀 1. Evolución respecto a Versión 1

1. **Ampliación Masiva del Presupuesto de Salida (Output Token Budget):**
   * Configurado a **8,192 tokens** (`-n 8192`), resolviendo el cuello de botella detectado en la versión 1 (donde el modelo Original se quedó atrapado pensando en la pregunta 15 al superar los 1,024 tokens).
2. **Expansión de la Ventana de Contexto:**
   * Ventana ampliada a **16,384 tokens** (`-c 16384`) con cuantización de KV cache `-ctk q4_0 -ctv q4_0` para albergar cómodamente el razonamiento profundo sin comprometer la VRAM de la RTX 5080.
3. **Aislamiento Total de Contexto (Contexto Cero por Pregunta):**
   * Cada pregunta corre en un proceso independiente de `llama-cli`.
   * Al emitir el resultado, el proceso muere y libera el 100% de la memoria y tensores.
   * La siguiente pregunta inicia estrictamente desde cero (0 tokens residuales en historial).
4. **Escala Completa:**
   * Evaluación de las **100 preguntas completas** del dataset oficial `openai/gsm8k`.
   * Guardado incremental en caliente tras cada pregunta.
