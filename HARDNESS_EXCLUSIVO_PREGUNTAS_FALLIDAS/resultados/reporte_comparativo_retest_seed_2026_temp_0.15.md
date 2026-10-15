# 📊 REPORTE DE RETEST: 8 PREGUNTAS FALLIDAS (GSM8K)

**Semilla Evaluada:** `2026` | **Temperatura:** `0.15`
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, Precisión KV Cache: FP16

### 🏆 Puntuaciones en el Retest (8 Preguntas Clave)

| Modelo | Aciertos Retest | Precisión Retest | Corrida Original V3 (100 Qs) |
| :--- | :---: | :---: | :---: |
| **Original** | **4 / 8** | **50.0%** | 96.0% (96/100) |
| **Abliterado_V2** | **3 / 8** | **37.5%** | 96.0% (96/100) |
| **Xiaomi_MiMo** | **5 / 8** | **62.5%** | 96.0% (96/100) |

---

### 🔍 Comparativa Detallada Pregunta por Pregunta

| # | Esperado | Original (Prev -> Retest) | Abliterado V2 (Prev -> Retest) | Xiaomi MiMo (Prev -> Retest) |
| :-: | :---: | :---: | :---: | :---: |
| 13 | `13` | ❌ `12` ➔ `12` (101.4s) | ❌ `12` ➔ `12` (134.9s) | ❌ `12` ➔ `12` (5.5s) |
| 38 | `2` | ✅ `0` ➔ `2` (224.4s) | ❌ `2` ➔ `0` (176.5s) | ❌ `0` ➔ `0` (3.8s) |
| 46 | `104` | ❌ `0.4` ➔ `14` (377.6s) | ✅ `104` ➔ `104` (181.4s) | ✅ `104` ➔ `104` (6.3s) |
| 63 | `25000` | ✅ `25000` ➔ `25000` (105.8s) | ✅ `25000` ➔ `25000` (108.0s) | ❌ `2500` ➔ `2500` (8.4s) |
| 74 | `255` | ❌ `255` ➔ `265` (249.3s) | ❌ `5` ➔ `265` (217.7s) | ✅ `255` ➔ `255` (7.0s) |
| 76 | `60` | ✅ `60` ➔ `60` (59.1s) | ✅ `60` ➔ `60` (53.4s) | ✅ `7.5` ➔ `60` (5.2s) |
| 86 | `44` | ✅ `44` ➔ `44` (105.9s) | ❌ `48` ➔ `48` (339.0s) | ✅ `44` ➔ `44` (5.8s) |
| 94 | `36` | ❌ `1.10` ➔ `36.36` (180.8s) | ❌ `1.10` ➔ `36.36` (165.1s) | ✅ `36` ➔ `36` (7.0s) |

---

### 📝 Notas y Diagnóstico de Semilla
- Si una pregunta pasó de ❌ a ✅, confirma que el error previo fue estocástico (mala semilla).
- Si persiste en ❌ con el mismo número, confirma una limitación epistémica o ambigüedad intrínseca en el problema.
