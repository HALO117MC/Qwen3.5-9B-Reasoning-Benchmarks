# 📊 REPORTE DE RETEST AUDITADO: 8 PREGUNTAS FALLIDAS (GSM8K)

**Estado de Auditoría:** ✅ PARSER CORREGIDO (Sin contaminación de telemetría `llama-cli` ni confusión con thinking)

**Semilla Evaluada:** `2026` | **Temperatura:** `0.3`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16 puro

### 🏆 Puntuaciones Reales en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **3 / 8** | **37.5%** | 96.0% (96/100) |
| **Abliterado_V2** | **4 / 8** | **50.0%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **5 / 8** | **62.5%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (V3 ➔ Retest) | Abliterado V2 (V3 ➔ Retest) | Xiaomi MiMo (V3 ➔ Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (96.2s) | ❌ `12` ➔ `12` (108.1s) | ❌ `12` ➔ `90` (4.6s) |
| 38 | `2` | ✅ `0` ➔ `2` (112.2s) | ✅ `2` ➔ `2` (105.0s) | ❌ `0` ➔ `0` (5.7s) |
| 46 | `104` | ❌ `0.4` ➔ `2` (278.1s) | ❌ `104` ➔ `2` (286.6s) | ✅ `104` ➔ `104` (4.5s) |
| 63 | `25000` | ❌ `25000` ➔ `5` (291.1s) | ✅ `25000` ➔ `25000` (128.2s) | ❌ `2500` ➔ `2500` (3.1s) |
| 74 | `255` | ✅ `255` ➔ `255` (222.8s) | ✅ `5` ➔ `255` (71.9s) | ✅ `255` ➔ `255` (5.2s) |
| 76 | `60` | ✅ `60` ➔ `60` (75.7s) | ✅ `60` ➔ `60` (99.1s) | ✅ `7.5` ➔ `60` (4.8s) |
| 86 | `44` | ❌ `44` ➔ `2` (289.8s) | ❌ `48` ➔ `11` (290.3s) | ✅ `44` ➔ `44` (5.3s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (215.1s) | ❌ `1.10` ➔ `38` (288.3s) | ✅ `36` ➔ `36` (5.9s) |

---

### 🔬 Hallazgos y Aclaraciones Críticas
1. **¿Fallaron todos realmente?** **NO.** Los modelos NO fallaron en masa. El reporte inicial mostró 0/8 porque el parser anterior tomaba el número de la velocidad de inferencia de `llama-cli` (`Generation: 62.3 t/s`) como la predicción.
2. **¿Se dejó la etiqueta `<think>` en Xiaomi MiMo?** **SÍ, 100% activa.** Xiaomi MiMo recibió `<think>\n` explícito en su prompt, lo que le permitió razonar a alta velocidad (promedio ~5 segundos por pregunta) y obtener **5 de 8 aciertos (62.5%)** en las preguntas más difíciles.
3. **Rendimiento de Abliterado V2:** Obtuvo **4 de 8 aciertos (50.0%)**, resolviendo Q38, Q63, Q74 y Q76 con razonamiento matemático impecable.
4. **Rendimiento de Original:** Obtuvo **3 de 8 aciertos (37.5%)**, resolviendo Q38, Q74 y Q76.
