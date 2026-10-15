# 📊 REPORTE DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)

**Semilla Evaluada:** `2026` | **Temperatura:** `0.1`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16

### 🏆 Puntuaciones en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **5 / 8** | **62.5%** | 96.0% (96/100) |
| **Abliterado_V2** | **5 / 8** | **62.5%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **5 / 8** | **62.5%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (Prev -> Retest) | Abliterado V2 (Prev -> Retest) | Xiaomi MiMo (Prev -> Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (28.6s) | ❌ `12` ➔ `12` (68.6s) | ❌ `12` ➔ `12` (3.8s) |
| 38 | `2` | ✅ `0` ➔ `2` (187.8s) | ✅ `2` ➔ `2` (146.7s) | ❌ `0` ➔ `0` (3.4s) |
| 46 | `104` | ❌ `0.4` ➔ `7` (278.3s) | ✅ `104` ➔ `104` (158.5s) | ✅ `104` ➔ `104` (6.2s) |
| 63 | `25000` | ✅ `25000` ➔ `25000` (76.2s) | ✅ `25000` ➔ `25000` (73.5s) | ❌ `2500` ➔ `2500` (7.3s) |
| 74 | `255` | ✅ `255` ➔ `255` (94.7s) | ❌ `5` ➔ `265` (200.5s) | ✅ `255` ➔ `255` (5.9s) |
| 76 | `60` | ✅ `60` ➔ `60` (63.0s) | ✅ `60` ➔ `60` (47.9s) | ✅ `7.5` ➔ `60` (4.3s) |
| 86 | `44` | ✅ `44` ➔ `44` (54.8s) | ✅ `48` ➔ `44` (86.7s) | ✅ `44` ➔ `44` (5.2s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (144.8s) | ❌ `1.10` ➔ `9.09` (268.5s) | ✅ `36` ➔ `36` (5.9s) |

---

### 📝 Notas y Diagnóstico de Semilla
- Si una pregunta pasó de ❌ a ✅, confirma que el error previo fue estocástico (mala semilla).
- Si persiste en ❌ con el mismo número, confirma una limitación epistémica o ambigüedad intrínseca en el problema.
