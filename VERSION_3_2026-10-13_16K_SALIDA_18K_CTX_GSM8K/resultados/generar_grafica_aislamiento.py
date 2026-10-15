import matplotlib.pyplot as plt
import numpy as np

# Configurar estilo visual oscuro de alta fidelidad
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9), dpi=160, gridspec_kw={'width_ratios': [1.2, 1]})
fig.patch.set_facecolor('#0b0f19')
ax1.set_facecolor('#111827')
ax2.set_facecolor('#111827')

# ==============================================================================
# SUBPLOT 1: MATRIZ DE AISLAMIENTO DE FALLOS (LAS 8 PREGUNTAS CON ERRORES)
# ==============================================================================
# Datos de las 8 preguntas
q_labels = [
    'Q13: Limonero\n(Todos fallaron)',
    'Q38: Legos de John\n(Solo triunfo Abliterado)',
    'Q46: Blog Meredith\n(Solo fallo Original)',
    'Q63: Pension Marcy\n(Solo fallo MiMo)',
    'Q74: Celulares Shiela\n(Solo fallo Abliterado)',
    'Q76: Arena de Luke\n(Solo fallo MiMo)',
    'Q86: Colcha de Gene\n(Solo fallo Abliterado)',
    'Q94: Vallas de Lee\n(Solo triunfo MiMo)'
]

models = ['Qwen Original', 'Abliterado V2', 'Xiaomi MiMo']

# Matriz: 1 = Acerto (Verde), 0 = Fallo (Rojo)
# Filas: Modelos (Original, Abliterado, MiMo), Columnas: Preguntas
matrix = np.array([
    [0, 0, 0, 1, 1, 1, 1, 0],  # Original
    [0, 1, 1, 1, 0, 1, 0, 0],  # Abliterado V2
    [0, 0, 1, 0, 1, 0, 1, 1]   # Xiaomi MiMo
])

# Valores predichos vs esperados
cell_texts = [
    ['12 vs 13\n(88.7s)', '0 vs 2\n(158.2s)', '0.4 vs 104\n(291.3s)', '25k vs 25k\n(65.4s)', '255 vs 255\n(90.7s)', '60 vs 60\n(46.1s)', '44 vs 44\n(146.9s)', '1.1 vs 36\n(280.3s)'],
    ['12 vs 13\n(69.5s)', '2 vs 2\n(128.3s)', '104 vs 104\n(166.7s)', '25k vs 25k\n(69.3s)', '5 vs 255\n(274.9s)', '60 vs 60\n(39.6s)', '48 vs 44\n(124.6s)', '1.1 vs 36\n(288.2s)'],
    ['12 vs 13\n(4.8s)',  '0 vs 2\n(4.8s)',   '104 vs 104\n(5.9s)',   '2.5k vs 25k\n(6.3s)', '255 vs 255\n(5.8s)',  '7.5 vs 60\n(4.4s)',  '44 vs 44\n(6.4s)',   '36 vs 36\n(3.9s)']
]

# Dibujar matriz tipo heatmap
cmap = plt.cm.colors.ListedColormap(['#ef4444', '#10b981'])  # Rojo para fallo, Verde para acierto
im = ax1.imshow(matrix, cmap=cmap, aspect='auto', alpha=0.85)

# Configurar ejes
ax1.set_xticks(np.arange(len(q_labels)))
ax1.set_yticks(np.arange(len(models)))
ax1.set_xticklabels(q_labels, fontsize=9.5, fontweight='bold', color='#e2e8f0', rotation=25, ha='right')
ax1.set_yticklabels(models, fontsize=12, fontweight='bold', color='#ffffff')

# Anotar cada celda con el texto del resultado y tiempo
for i in range(len(models)):
    for j in range(len(q_labels)):
        status = 'ACERTO' if matrix[i, j] == 1 else 'FALLO'
        color_text = '#ffffff'
        ax1.text(j, i, f"[{status}]\n{cell_texts[i][j]}", ha='center', va='center', 
                 fontsize=8.5, fontweight='bold', color=color_text)

ax1.set_title('MATRIZ COMPARATIVA DE LAS 8 PREGUNTAS CON FALLOS\n(Verde = Acierto Exitoso | Rojo = Respuesta Incorrecta)', 
              fontsize=13, fontweight='bold', color='#38bdf8', pad=15)
ax1.grid(color='#1e293b', linestyle='-', linewidth=2)

# ==============================================================================
# SUBPLOT 2: AISLAMIENTO POR CATEGORIA Y CAUSA (TRUNCAMIENTO VS ERROR LOGICO)
# ==============================================================================
categories = [
    'Fallaron TODOS (Q13)\nAmbiguedad semantica',
    'Solo triunfo ABLITERADO (Q38)\nSupero la trampa de los legos',
    'Solo triunfo MIMO (Q94)\nResolvio vallas en 3.9s',
    'Solo fallo ORIGINAL (Q46)\nConfundio horas y fracciones',
    'Solo fallo ABLITERADO (Q74, Q86)\nDesglose mensual y colcha',
    'Solo fallo MIMO (Q63, Q76)\nOmitio cero y evaporacion',
    'TRUNCAMIENTO / CORTE DE TOKENS\n(Falta de contexto o salida)'
]

conteos = [1, 1, 1, 1, 2, 2, 0]
colores_cat = ['#8b5cf6', '#10b981', '#f59e0b', '#3b82f6', '#059669', '#d97706', '#ef4444']

y_pos = np.arange(len(categories))
bars = ax2.barh(y_pos, conteos, color=colores_cat, height=0.6, edgecolor='#ffffff', alpha=0.9)

for bar in bars:
    w = bar.get_width()
    y = bar.get_y() + bar.get_height() / 2
    if w == 0:
        ax2.text(0.1, y, '0 (CERO CORTES - 100% RESPUESTAS TERMINADAS)', color='#4ade80', fontweight='bold', va='center', fontsize=9.5)
    else:
        ax2.text(w + 0.08, y, f'{int(w)} pregunta(s)', color='#ffffff', fontweight='bold', va='center', fontsize=10)

ax2.set_yticks(y_pos)
ax2.set_yticklabels(categories, fontsize=9.5, fontweight='bold', color='#cbd5e1')
ax2.set_xlim(0, 3.2)
ax2.set_xlabel('Numero de Preguntas Afectadas', fontsize=11, color='#94a3b8')
ax2.set_title('AISLAMIENTO DE ERRORES: CAUSA Y GANADOR\n¿Hubo cortes o concluyeron con calculo erroneo?', 
              fontsize=13, fontweight='bold', color='#38bdf8', pad=15)
ax2.grid(axis='x', linestyle='--', alpha=0.2, color='#94a3b8')

# Titulo principal y pie
fig.suptitle('AUDITORIA FORENSE GSM8K: AISLAMIENTO DE LAS 8 PREGUNTAS CLAVE DEL TRÍO QWEN 3.5 9B', 
             fontsize=16, fontweight='bold', color='#f8fafc', y=0.98)
plt.figtext(0.5, 0.02, 
            'CONCLUSION CLAVE: Ningun modelo se corto (0% truncamientos). Todos terminaron normalmente con <|im_end|>. Cada fallo fue estrictamente de interpretacion logica o aritmetica.', 
            ha='center', fontsize=10.5, style='italic', color='#94a3b8')

plt.tight_layout(rect=[0, 0.05, 1, 0.94])

out1 = '/home/genelinux01/Caja_Fuerte_IDE/Umbral/Config_Aislada/.gemini/antigravity/brain/8f9058ba-55a5-4fc0-a68b-5b60f0f14101/grafica_aislamiento_fallos_gsm8k.png'
out2 = '/home/genelinux01/IAPower/Herramientas_IA/ACCESORIOS_PARA_LLM/LAB-PRUEBAS-TODO-TIPO/HARDNES-PRUEBAS/HARDEN-PRUEBA-QWEN3-5-9B/VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/grafica_aislamiento_fallos_gsm8k.png'

plt.savefig(out1, facecolor=fig.get_facecolor(), edgecolor='none')
plt.savefig(out2, facecolor=fig.get_facecolor(), edgecolor='none')
print("Grafica de aislamiento generada con exito.")
