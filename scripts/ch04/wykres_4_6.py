import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# ---------------------------------------------------------
# 1. Dane z tabeli 4.7
# ---------------------------------------------------------
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']
means = [127.99, 128.02, 128.02]
stds = [8.00, 8.01, 8.02]
mins = [95, 92, 95]
maxs = [163, 163, 162]

# Kolory zgodne z oryginałem
colors = ['#3182bd', '#e377c2', '#ff7f0e']

# ---------------------------------------------------------
# 2. Konfiguracja Wykresu
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))

# Linia Idealna (128 bitów)
ax.axhline(128, color='black', linestyle='--', linewidth=1.5)
ax.text(0.95, 130, 'Ideal: 128 bitów (50%)', ha='right', fontsize=10, style='italic')

x_positions = [1, 2, 3]
box_width = 0.6

for i, x in enumerate(x_positions):
    # --- Whiskery (Wąsy) od Min do Max ---
    ax.plot([x, x], [mins[i], maxs[i]], color=colors[i], linewidth=1.5)
    
    # --- Czapeczki wąsów (Caps) ---
    cap_width = 0.15
    ax.plot([x - cap_width, x + cap_width], [mins[i], mins[i]], color=colors[i], linewidth=1.5)
    ax.plot([x - cap_width, x + cap_width], [maxs[i], maxs[i]], color=colors[i], linewidth=1.5)
    
    # --- Pudełko (Box) ---
    # Zgodnie z danymi: Box = Średnia +/- Odchylenie Standardowe
    y_bottom = means[i] - stds[i]
    y_top = means[i] + stds[i]
    
    rect = Rectangle((x - box_width/2, y_bottom), box_width, y_top - y_bottom, 
                     facecolor=colors[i], edgecolor=colors[i], linewidth=1)
    ax.add_patch(rect)
    
    # --- Linia Średniej (biała linia w środku pudełka) ---
    ax.plot([x - box_width/2, x + box_width/2], [means[i], means[i]], color='white', linewidth=2)
    
    # --- Adnotacje tekstowe (μ i σ) pod wykresem ---
    ax.text(x, mins[i] - 4, f'μ={means[i]:.2f}\nσ={stds[i]:.2f}', 
            ha='center', va='top', fontsize=10, color=colors[i], fontweight='bold')

# ---------------------------------------------------------
# 3. Etykiety i Styl
# ---------------------------------------------------------
ax.set_xticks(x_positions)
ax.set_xticklabels(algorithms, fontsize=11)
ax.set_xlabel('Algorytm XOF', fontsize=11, fontweight='bold')
ax.set_ylabel('Liczba zmienionych bitów (z 256)', fontsize=11)

ax.set_title('Rozkład efektu lawinowego (SAC) - odległość Hamminga\nprzy zmianie 1 bitu wejścia (wyjście 256 bitów, 128 000 prób)', 
             fontsize=13, pad=20)

# Ustawienie zakresu osi Y
ax.set_ylim(90, 170)
ax.grid(axis='y', linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()
