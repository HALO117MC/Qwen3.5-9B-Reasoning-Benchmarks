import matplotlib.pyplot as plt
import numpy as np

# Configurar estilo visual oscuro moderno
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), dpi=150)
fig.patch.set_facecolor('#0f111a')
ax1.set_facecolor('#1a1c29')
ax2.set_facecolor('#1a1c29')

# --- SUBPLOT 1: Tiempos de las preguntas falladas y comparativa ---
questions = ['Q13\nLimonero', 'Q38\nLegos', 'Q46\nHoras Blog', 'Q63\nPension', 'Q74\nCelulares', 'Q76\nArena', 'Q86\nColcha', 'Q94\nVallas']
x = np.arange(len(questions))
width = 0.28

# Tiempos exactos en segundos
t_orig = [88.7, 158.2, 291.3, 65.4, 90.7, 46.1, 146.9, 280.3]
t_abli = [69.5, 128.3, 166.7, 69.3, 274.9, 39.6, 124.6, 288.2]
t_mimo = [4.8, 4.8, 5.9, 6.3, 5.8, 4.4, 6.4, 3.9]

# Estados: True = Acertó, False = Falló
s_orig = [False, False, False, True, True, True, True, False]
s_abli = [False, True, True, True, False, True, False, False]
s_mimo = [False, False, True, False, True, False, True, True]

bars1 = ax1.bar(x - width, t_orig, width, label='Qwen Original (96%)', color='#3b82f6', alpha=0.9, edgecolor='#1d4ed8')
bars2 = ax1.bar(x, t_abli, width, label='Abliterado V2 (96%)', color='#10b981', alpha=0.9, edgecolor='#047857')
bars3 = ax1.bar(x + width, t_mimo, width, label='Xiaomi MiMo (96%)', color='#f59e0b', alpha=0.9, edgecolor='#b45309')

# Etiquetas de acierto / fallo encima de cada barra sin emojis para evitar advertencias de fuentes
for i in range(len(questions)):
    # Original
    mark1 = 'FALLO' if not s_orig[i] else 'OK'
    c1 = '#f87171' if not s_orig[i] else '#60a5fa'
    ax1.text(x[i] - width, t_orig[i] + 7, f"{mark1}\n{t_orig[i]:.0f}s", ha='center', va='bottom', fontsize=8, color=c1, fontweight='bold')
    # Abliterado
    mark2 = 'FALLO' if not s_abli[i] else 'OK'
    c2 = '#f87171' if not s_abli[i] else '#34d399'
    ax1.text(x[i], t_abli[i] + 7, f"{mark2}\n{t_abli[i]:.0f}s", ha='center', va='bottom', fontsize=8, color=c2, fontweight='bold')
    # MiMo
    mark3 = 'FALLO' if not s_mimo[i] else 'OK'
    c3 = '#f87171' if not s_mimo[i] else '#fbbf24'
    ax1.text(x[i] + width, t_mimo[i] + 7, f"{mark3}\n{t_mimo[i]:.1f}s", ha='center', va='bottom', fontsize=8, color=c3, fontweight='bold')

ax1.set_title('Tiempo de Inferencia en las 8 Preguntas con Fallos\n(OK = Acierto | FALLO = Error)', fontsize=13, fontweight='bold', pad=15, color='#ffffff')
ax1.set_xticks(x)
ax1.set_xticklabels(questions, fontsize=10, fontweight='bold', color='#e2e8f0')
ax1.set_ylabel('Tiempo de Inferencia (Segundos)', fontsize=11, color='#cbd5e1')
ax1.set_ylim(0, 360)
ax1.grid(axis='y', linestyle='--', alpha=0.2, color='#94a3b8')
ax1.legend(loc='upper right', framealpha=0.8, facecolor='#1e293b', edgecolor='#334155')

# --- SUBPLOT 2: Causa Raíz del Fallo: Truncamiento vs Error de Contenido ---
causes = [
    'Truncamiento por Tokens\n(-n 16000 / -c 18000)',
    'Ambiguedad Semantica\nde Etiqueta (Q13)',
    'Trampa Semantica\n(Q38 Legos de John)',
    'Error de Unidades\no Fracciones (Q46)',
    'Error de Escala/Ceros\n(Q63 Marcy 2.5k vs 25k)',
    'Calculo Complejo / Bucle\n(Q74, Q86, Q94)'
]
occurrences = [0, 3, 2, 1, 1, 4]
colors = ['#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#eab308']

bars_c = ax2.barh(causes, occurrences, color=colors, alpha=0.9, edgecolor='#ffffff', height=0.55)
for bar in bars_c:
    w = bar.get_width()
    ax2.text(w + 0.1, bar.get_y() + bar.get_height()/2, f" {int(w)} eventos" if w > 0 else " 0 (CERO TRUNCAMIENTOS)", 
             ha='left', va='center', fontsize=11, fontweight='bold', 
             color='#22c55e' if w == 0 else '#ffffff')

ax2.set_title('Causa Raiz de los Fallos (Total: 12 Fallos en 300 Pruebas)\n¿Se corto el modelo o concluyo con error?', fontsize=13, fontweight='bold', pad=15, color='#ffffff')
ax2.set_xlabel('Numero de Ocurrencias en el Trio Evaluado', fontsize=11, color='#cbd5e1')
ax2.set_xlim(0, 5)
ax2.grid(axis='x', linestyle='--', alpha=0.2, color='#94a3b8')

# Nota de pie de gráfico
fig.suptitle('AUDITORIA DE FALLOS Y TIEMPOS: BENCHMARK GSM8K (100 PREGUNTAS) - TRIO QWEN 3.5 9B (Q8_0)', 
             fontsize=15, fontweight='bold', color='#38bdf8', y=0.98)
plt.figtext(0.5, 0.02, 
            'CONCLUSION CIENTIFICA: 0% Truncamiento. Todos los modelos concluyeron con su token de fin natural <|im_end|>. El 100% de los fallos fue por interpretacion logica/semantica.', 
            ha='center', fontsize=10, style='italic', color='#94a3b8')

plt.tight_layout(rect=[0, 0.05, 1, 0.94])

out_path1 = './artifacts/8f9058ba-55a5-4fc0-a68b-5b60f0f14101/grafica_auditoria_fallos_100_gsm8k.png'
out_path2 = './VERSION_3_2026-10-13_16K_SALIDA_18K_CTX_GSM8K/resultados/grafica_auditoria_fallos_100_gsm8k.png'

plt.savefig(out_path1, facecolor=fig.get_facecolor(), edgecolor='none')
plt.savefig(out_path2, facecolor=fig.get_facecolor(), edgecolor='none')
print("Grafica generada perfectamente.")
