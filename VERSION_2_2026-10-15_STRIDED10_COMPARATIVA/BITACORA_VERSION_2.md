# Bitácora de Experimentación: Harness V2.1 (10 Tareas Salteadas de 10 en 10)
**Fecha:** 2026-10-15  
**Hardware:** NVIDIA GeForce RTX 5080 Laptop GPU (16 GB VRAM)  
**Entorno:** llama.cpp oficial v0.6.0 (commit b42b7e6d3)  
**Ruta del Harness:** `./VERSION_2_2026-10-15_STRIDED10_COMPARATIVA/`

---

## 1. Parámetros de Inferencia Aplicados
- **Ventana de Contexto (`-c`):** 18,000 tokens
- **Límite de Salida (`-n`):** 16,384 tokens
- **Inyección de Prefijo:** `<|im_start|>assistant\n<think>\n`
- **Cache KV:** Q4_0 (`-ctk q4_0 -ctv q4_0`)
- **Temperatura:** 0.0 (determinista)
- **Timeout por tarea:** 300 segundos

---

## 2. Resultados Globales y Auditoría Forense

| Modelo | Aciertos | Precisión | Tiempo Total | Tiempo Promedio |
| :--- | :---: | :---: | :---: | :---: |
| **Qwen3.5-9B Original Q8_0** | **9 / 10** | **90.0%** | 528.5 s (~8.8 min) | 52.85 s |
| **Qwen3.5-9B Abliterado V2 Q8_0** | **9 / 10** | **90.0%** | 586.2 s (~9.7 min) | 58.62 s |
| **Xiaomi MiMo-V2.6-Distill-Qwen-9B Q8_0** | **9 / 10** | **90.0%** | **74.6 s (~1.2 min)** | **7.46 s** |

### Conclusiones Principales:
1. **Velocidad de Xiaomi MiMo:** Es **7.4 veces más rápido** que el modelo Original y el Abliterado, resolviendo las mismas 10 tareas con la misma tasa de acierto (90%).
2. **Eliminación del Cuello de Botella de Tokens:** Al ampliar de 1024 a 16,384 tokens, el modelo Original y el Abliterado resolvieron correctamente problemas de razonamiento multi-paso como la Tarea 21 (15) y Tarea 51 (294).
3. **Tendencia a Loops en Modelos Base:** Original y Abliterado sufrieron un timeout de 300s cada uno (T41 y T11 respectivamente) debido a bucles de deliberación circular interna al no contar con regularizador de repetición.
4. **Comportamiento Agéntico de MiMo:** En la Tarea 71, MiMo intentó delegar pasos mediante `<tool_call>`, lo que confirma su perfil agéntico nativo frente a los modelos puramente generadores de texto.
