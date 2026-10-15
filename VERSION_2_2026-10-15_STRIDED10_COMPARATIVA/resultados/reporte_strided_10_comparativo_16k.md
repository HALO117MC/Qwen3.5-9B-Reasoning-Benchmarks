# 📊 Reporte Comparativo Global V2.1: Qwen 3.5 9B Family (Strided 10 Tasks)
**Entorno de Ejecución:** RTX 5080 (16 GB VRAM) | **Inferencia:** llama.cpp oficial v0.6.0
**Parámetros:** Contexto = 18,000 tokens (`-c 18000`) | Salida Máx = 16,384 tokens (`-n 16384`) | Prefijo = `<|im_start|>assistant\n<think>\n`
**Dataset:** GSM8K Test Suite (Muestreo cada 10 tareas: 1, 11, 21, 31, 41, 51, 61, 71, 81, 91)

---

## 🏆 1. Resumen Ejecutivo y Métricas Consolidadas

| Métrica / Parámetro | Qwen3.5-9B Original Q8 | Qwen3.5-9B Abliterado V2 Q8 | Xiaomi MiMo-V2.6 Distill Q8 |
| :--- | :---: | :---: | :---: |
| **Aciertos Oficiales (Auditados)** | **9 / 10** | **9 / 10** | **9 / 10** |
| **Precisión Global** | **90.0%** | **90.0%** | **90.0%** |
| **Tiempo Total (10 tareas)** | 528.5 s (~8.8 min) | 586.2 s (~9.7 min) | **74.6 s (~1.2 min)** |
| **Velocidad Promedio por Tarea** | 52.85 s | 58.62 s | **7.46 s (7.4x más veloz)** |
| **Rendimiento Generación** | ~48 - 51 t/s | ~48 - 51 t/s | **~50 - 52 t/s** |
| **Longitud Media Razonamiento**| 1,500 – 3,500 tokens | 1,800 – 4,000 tokens | **150 – 400 tokens** |
| **Causa de Fallo** | Timeout (300s en T41) | Timeout (300s en T11) | Emisión `<tool_call>` (T71) |

---

## 📋 2. Tabla Detallada Tarea por Tarea

| # Tarea | Enunciado Sintético | Valor Esperado | Original Q8 | Abliterado V2 Q8 | Xiaomi MiMo Q8 |
| :-: | :--- | :-: | :---: | :---: | :---: |
| **01** | Venta de pasteles y donas | `18` | ✅ **18** *(8.8s)* | ✅ **18** *(10.1s)* | ✅ **18** *(4.0s)* |
| **11** | Descargas acumuladas software | `366` | ✅ **366** *(23.1s)* | ❌ `Timeout` *(300.0s)* | ✅ **366** *(5.6s)* |
| **21** | Mezcla de jugos y derrame | `15` | ✅ **15** *(41.9s)* | ✅ **15** *(49.5s)* | ✅ **15** *(17.6s)* 🔍* |
| **31** | Ratio de edades de Allen y Darrell | `109` | ✅ **109** *(24.3s)* | ✅ **109** *(24.8s)* | ✅ **109** *(8.2s)* |
| **41** | Edades relativas de iPhones | `8` | ❌ `Timeout` *(300.0s)* | ✅ **8** *(65.8s)* | ✅ **8** *(5.5s)* |
| **51** | Producción granja de huevos semanal | `294` | ✅ **294** *(26.6s)* | ✅ **294** *(35.7s)* | ✅ **294** *(10.0s)* 🔍* |
| **61** | Distancia recorrida en trayectos | `17` | ✅ **17** *(39.5s)* | ✅ **17** *(29.5s)* | ✅ **17** *(10.5s)* |
| **71** | Clases de baile de Judy | `7425` | ✅ **7425** *(31.9s)* | ✅ **7425** *(39.3s)* | ❌ `<tool_call>` *(3.3s)* ⚙️** |
| **81** | Puntos en juego de mesa | `10` | ✅ **10** *(14.3s)* | ✅ **10** *(13.4s)* | ✅ **10** *(4.8s)* |
| **91** | Conteo de páginas leídas | `225` | ✅ **225** *(18.2s)* | ✅ **225** *(18.1s)* | ✅ **225** *(5.1s)* |

> **Notas de Auditoría Técnica Forense:**
> - 🔍* **Tareas 21 y 51 en Xiaomi MiMo:** En el análisis del texto crudo de salida, Xiaomi resolvió ambas tareas con exactitud perfecta (`**Answer: 15 liters of water**` y `Lloyd makes **$294** per week on eggs`). El parser inicial había tomado la telemetría final de `llama-cli` (`Generation: 50.4 t/s` y `50.9 t/s`), pero la evidencia matemática generada por el modelo es 100% correcta.
> - ⚙️** **Tarea 71 en Xiaomi MiMo:** MiMo tiene destilado entrenamiento nativo agéntico con function calling. Al leer el problema, en lugar de responder texto intentó invocar un subproceso cognitivo mediante `<tool_call><function=think><parameter=steps>5</parameter></function></tool_call>`, lo que cerró el stream de inferencia prematuramente.
> - ⏱️ **Timeouts en Original (T41) y Abliterado (T11):** Ambos modelos entraron en sobre-razonamiento circular dentro de `<think>` generando más de 14,000 tokens en un solo turno hasta alcanzar el corte de seguridad de 300 segundos.

---

## 💡 3. Conclusiones y Comparativa Clave

1. **Eficiencia y Velocidad de Xiaomi MiMo (Superioridad Práctica):**
   - MiMo alcanzó el **mismo 90% de precisión** que el modelo Original y el Abliterado, pero resolvió la suite completa en **1 minuto y 14 segundos**, comparado con los **casi 10 minutos** que requirieron Original y Abliterado.
   - Es **7.4 veces más rápido** en resolución de problemas complejos porque sus cadenas de pensamiento están optimizadas para ir al grano sin divagaciones.

2. **Impacto del Límite de 16,384 Tokens:**
   - La corrección del límite de tokens solicitada fue un acierto total: permitió que Original y Abliterado pasaran de fallar casi la mitad del examen a obtener **90% de precisión**, ya que sus respuestas requerían entre 1,500 y 3,500 tokens de deliberación previa.

3. **Comportamiento Agéntico de MiMo:**
   - La única tarea donde MiMo no entregó el número final (Tarea 71) se debió a su arquitectura agéntica orientada a herramientas (`<tool_call>`), reflejando que está diseñado como un agente autónomo de toma de decisiones y no como un simple generador de texto plano.
