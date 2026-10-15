# 🏆 REPORTE MAESTRO: BARRIDO TÉRMICO COMPLETO SOTA (GSM8K)

**Semilla:** `2026` | **Modelos:** Original, Abliterado V2, Xiaomi MiMo (`<think> ON`)
**Parámetros:** Contexto `-c 18000`, Salida `-n 16000`, KV Cache FP16 puro

### 📈 Tabla Resumen de Puntuaciones (% Aciertos sobre 8 Preguntas Clave)

| Temperatura | Original | Abliterado V2 | Xiaomi MiMo | Estado / Hallazgo |
| :---: | :---: | :---: | :---: | :--- |
| `T = 0.0` | **4/8** (50.0%) | **4/8** (50.0%) | **4/8** (50.0%) | Estable |
| `T = 0.1` | **5/8** (62.5%) | **5/8** (62.5%) | **5/8** (62.5%) | 🔥 **ZONA SOTA (Triple empate 62.5%+)** |
| `T = 0.12` | **5/8** (62.5%) | **4/8** (50.0%) | **5/8** (62.5%) | Estable |
| `T = 0.15` | **4/8** (50.0%) | **3/8** (37.5%) | **5/8** (62.5%) | Estable |
| `T = 0.18` | **6/8** (75.0%) | **4/8** (50.0%) | **5/8** (62.5%) | 💎 **PUNTO SOTA MÁXIMO** |
| `T = 0.2` | **4/8** (50.0%) | **5/8** (62.5%) | **5/8** (62.5%) | Estable |
| `T = 0.3` | **3/8** (37.5%) | **4/8** (50.0%) | **5/8** (62.5%) | ⚠️ Colapso de Original por calor |

---

### 🎯 Punto SOTA Identificado: Temperaturas [0.1, 0.18]
