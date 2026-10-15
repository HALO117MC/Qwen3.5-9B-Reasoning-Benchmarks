# 📊 REPORTE DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)

**Semilla Evaluada:** `2026` | **Temperatura:** `0.2`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16

### 🏆 Puntuaciones en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **4 / 8** | **50.0%** | 96.0% (96/100) |
| **Abliterado_V2** | **5 / 8** | **62.5%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **5 / 8** | **62.5%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (Prev -> Retest) | Abliterado V2 (Prev -> Retest) | Xiaomi MiMo (Prev -> Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (94.9s) | ❌ `12` ➔ `12` (75.0s) | ❌ `12` ➔ `12` (4.3s) |
| 38 | `2` | ✅ `0` ➔ `2` (130.8s) | ❌ `2` ➔ `0` (160.9s) | ❌ `0` ➔ `0` (3.4s) |
| 46 | `104` | ❌ `0.4` ➔ `4` (276.2s) | ✅ `104` ➔ `104` (80.2s) | ✅ `104` ➔ `104` (5.6s) |
| 63 | `25000` | ✅ `25000` ➔ `25000` (115.6s) | ✅ `25000` ➔ `25000` (83.7s) | ❌ `2500` ➔ `2500` (6.3s) |
| 74 | `255` | ❌ `255` ➔ `265` (129.4s) | ✅ `5` ➔ `255` (149.9s) | ✅ `255` ➔ `255` (5.7s) |
| 76 | `60` | ✅ `60` ➔ `60` (56.0s) | ✅ `60` ➔ `60` (42.1s) | ✅ `7.5` ➔ `60` (4.3s) |
| 86 | `44` | ✅ `44` ➔ `44` (191.8s) | ✅ `48` ➔ `44` (107.7s) | ✅ `44` ➔ `44` (3.5s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (266.8s) | ❌ `1.10` ➔ `36.36` (125.6s) | ✅ `36` ➔ `36` (7.4s) |

---

### 📝 Notas y Diagnóstico de Semilla
- Si una pregunta pasó de ❌ a ✅, confirma que el error previo fue estocástico (mala semilla).
- Si persiste en ❌ con el mismo número, confirma una limitación epistémica o ambigüedad intrínseca en el problema.
