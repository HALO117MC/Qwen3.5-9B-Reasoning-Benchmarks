# 📊 REPORTE DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)

**Semilla Evaluada:** `2026` | **Temperatura:** `0.18`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16

### 🏆 Puntuaciones en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **6 / 8** | **75.0%** | 96.0% (96/100) |
| **Abliterado_V2** | **4 / 8** | **50.0%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **5 / 8** | **62.5%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (Prev -> Retest) | Abliterado V2 (Prev -> Retest) | Xiaomi MiMo (Prev -> Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (77.4s) | ❌ `12` ➔ `12` (119.7s) | ❌ `12` ➔ `12` (5.2s) |
| 38 | `2` | ✅ `0` ➔ `2` (193.8s) | ❌ `2` ➔ `0` (131.3s) | ❌ `0` ➔ `0` (3.8s) |
| 46 | `104` | ✅ `0.4` ➔ `104` (258.9s) | ❌ `104` ➔ `44` (251.2s) | ✅ `104` ➔ `104` (6.9s) |
| 63 | `25000` | ✅ `25000` ➔ `25000` (138.5s) | ✅ `25000` ➔ `25000` (105.9s) | ❌ `2500` ➔ `2500` (7.9s) |
| 74 | `255` | ✅ `255` ➔ `255` (315.9s) | ✅ `5` ➔ `255` (154.0s) | ✅ `255` ➔ `255` (6.9s) |
| 76 | `60` | ✅ `60` ➔ `60` (51.5s) | ✅ `60` ➔ `60` (36.6s) | ✅ `7.5` ➔ `60` (5.0s) |
| 86 | `44` | ✅ `44` ➔ `44` (221.8s) | ✅ `48` ➔ `44` (227.9s) | ✅ `44` ➔ `44` (6.2s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (203.3s) | ❌ `1.10` ➔ `36.36` (392.4s) | ✅ `36` ➔ `36` (7.8s) |

---

### 📝 Notas y Diagnóstico de Semilla
- Si una pregunta pasó de ❌ a ✅, confirma que el error previo fue estocástico (mala semilla).
- Si persiste en ❌ con el mismo número, confirma una limitación epistémica o ambigüedad intrínseca en el problema.
