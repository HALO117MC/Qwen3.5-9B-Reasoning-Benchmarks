# 📊 Reporte Comparativo Triple: Qwen 3.5 9B Benchmark Oficial

**Dataset:** `openai/gsm8k` (Hugging Face Oficial) | **Muestras:** 15 | **Cuantización:** GGUF Q8_0

### 🏆 Puntuaciones Finales

| Modelo | Aciertos | Precisión | Estado |
| :--- | :---: | :---: | :---: |
| **Original** | 9/15 | **60.0%** | 🟢 Completado |
| **Abliterado_V2** | 9/15 | **60.0%** | 🟢 Completado |
| **Xiaomi_MiMo** | 12/15 | **80.0%** | 🟢 Completado |

---

### 📝 Desglose Pregunta por Pregunta

| # | Esperado | Original | Abliterado V2 | Xiaomi MiMo |
| :-: | :---: | :---: | :---: | :---: |
| 1 | `18` | ✅ `18` | ✅ `18` | ✅ `18` |
| 2 | `3` | ✅ `3` | ✅ `3` | ✅ `3` |
| 3 | `70000` | ❌ `80000` | ❌ `80000` | ✅ `70000` |
| 4 | `540` | ✅ `540` | ✅ `540` | ✅ `540` |
| 5 | `20` | ✅ `20` | ✅ `20` | ✅ `20` |
| 6 | `64` | ✅ `64` | ❌ `0.60` | ❌ `1` |
| 7 | `260` | ✅ `260` | ✅ `260` | ✅ `260` |
| 8 | `160` | ❌ `200` | ❌ `2` | ❌ `60` |
| 9 | `45` | ❌ `3` | ❌ `3` | ✅ `45` |
| 10 | `460` | ✅ `460` | ✅ `460` | ✅ `460` |
| 11 | `366` | ✅ `366` | ✅ `366` | ✅ `366` |
| 12 | `694` | ✅ `694` | ✅ `694` | ✅ `694` |
| 13 | `13` | ❌ `7` | ❌ `7` | ❌ `12` |
| 14 | `18` | ❌ `5` | ❌ `5` | ✅ `18` |
| 15 | `60` | ❌ `20` | ✅ `60` | ✅ `60` |
