# 📊 REPORTE DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)

**Semilla Evaluada:** `2026` | **Temperatura:** `0.12`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16

### 🏆 Puntuaciones en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **5 / 8** | **62.5%** | 96.0% (96/100) |
| **Abliterado_V2** | **4 / 8** | **50.0%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **5 / 8** | **62.5%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (Prev -> Retest) | Abliterado V2 (Prev -> Retest) | Xiaomi MiMo (Prev -> Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (52.0s) | ❌ `12` ➔ `12` (108.7s) | ❌ `12` ➔ `12` (4.3s) |
| 38 | `2` | ✅ `0` ➔ `2` (164.7s) | ❌ `2` ➔ `0` (173.9s) | ❌ `0` ➔ `0` (3.9s) |
| 46 | `104` | ❌ `0.4` ➔ `44` (386.9s) | ❌ `104` ➔ `2` (386.6s) | ✅ `104` ➔ `104` (7.5s) |
| 63 | `25000` | ✅ `25000` ➔ `25000` (94.1s) | ✅ `25000` ➔ `25000` (127.5s) | ❌ `2500` ➔ `2500` (8.8s) |
| 74 | `255` | ✅ `255` ➔ `255` (110.6s) | ✅ `5` ➔ `255` (250.0s) | ✅ `255` ➔ `255` (7.1s) |
| 76 | `60` | ✅ `60` ➔ `60` (51.3s) | ✅ `60` ➔ `60` (61.1s) | ✅ `7.5` ➔ `60` (5.2s) |
| 86 | `44` | ✅ `44` ➔ `44` (154.1s) | ✅ `48` ➔ `44` (190.7s) | ✅ `44` ➔ `44` (6.2s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (200.5s) | ❌ `1.10` ➔ `9.09` (388.5s) | ✅ `36` ➔ `36` (7.3s) |

---

### 📝 Notas y Diagnóstico de Semilla
- Si una pregunta pasó de ❌ a ✅, confirma que el error previo fue estocástico (mala semilla).
- Si persiste en ❌ con el mismo número, confirma una limitación epistémica o ambigüedad intrínseca en el problema.
