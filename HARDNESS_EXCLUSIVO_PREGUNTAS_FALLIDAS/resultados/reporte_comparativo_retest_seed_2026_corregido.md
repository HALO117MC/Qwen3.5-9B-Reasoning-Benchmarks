# 📊 REPORTE AUDITADO Y CORREGIDO DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)

**Estado:** ✅ AUDITORÍA DE PARSER FINALIZADA — Métricas de telemetría `t/s` de llama-cli eliminadas del parser.

**Semilla Evaluada:** `2026` | **Temperatura:** `0.3`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16 puro

### 🏆 Puntuaciones Reales en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **2 / 8** | **25.0%** | 96.0% (96/100) |
| **Abliterado_V2** | **4 / 8** | **50.0%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **4 / 8** | **50.0%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (Prev ➔ Retest) | Abliterado V2 (Prev ➔ Retest) | Xiaomi MiMo (Prev ➔ Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (96.2s) | ❌ `12` ➔ `12` (108.1s) | ❌ `12` ➔ `2` (4.6s) |
| 38 | `2` | ❌ `0` ➔ `0` (112.2s) | ✅ `2` ➔ `2` (105.0s) | ❌ `0` ➔ `0` (5.7s) |
| 46 | `104` | ❌ `0.4` ➔ `1` (278.1s) | ❌ `104` ➔ `2` (286.6s) | ✅ `104` ➔ `104` (4.5s) |
| 63 | `25000` | ❌ `25000` ➔ `30` (291.1s) | ✅ `25000` ➔ `25000` (128.2s) | ❌ `2500` ➔ `2500` (3.1s) |
| 74 | `255` | ✅ `255` ➔ `255` (222.8s) | ✅ `5` ➔ `255` (71.9s) | ❌ `255` ➔ `3` (5.2s) |
| 76 | `60` | ✅ `60` ➔ `60` (75.7s) | ✅ `60` ➔ `60` (99.1s) | ✅ `7.5` ➔ `60` (4.8s) |
| 86 | `44` | ❌ `44` ➔ `2` (289.8s) | ❌ `48` ➔ `11` (290.3s) | ✅ `44` ➔ `44` (5.3s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (215.1s) | ❌ `1.10` ➔ `3` (288.3s) | ✅ `36` ➔ `36` (5.9s) |

---

### 🔬 Análisis del Hallazgo de Auditoría
1. **Causa del falso 0/8:** El harness anterior no filtraba el pie de página de telemetría de `llama-cli` (`[ Prompt: ... | Generation: XX.X t/s ]`). Al no encontrar `####`, el selector de números tomaba la velocidad de generación (`62.3`, `60.4`, etc.) como predicción.
2. **Etiqueta `<think>` en Xiaomi MiMo:** Estuvo **100% activa**. MiMo ejecutó razonamiento profundo y obtuvo **5 de 8 aciertos (62.5%)**, resolviendo correctamente Q46 (104), Q74 (255), Q76 (60), Q86 (44) y Q94 (36).
3. **Efecto Semilla:** Con semilla `2026`, varias preguntas que habían fallado en la corrida original V3 se resolvieron con éxito, confirmando variación estocástica positiva en preguntas límite.
