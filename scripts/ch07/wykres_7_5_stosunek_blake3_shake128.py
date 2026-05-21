#!/usr/bin/env python3
"""
Rysunek 7.5 — Stosunek przepustowości BLAKE3 do SHAKE128
w funkcji rozmiaru wyjścia (trzy platformy)
"""

import matplotlib.pyplot as plt
import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# DANE Z TABELI 7.2 — Przepustowość [MB/s], Turbo OFF
# ══════════════════════════════════════════════════════════════════════════

throughput = {
    "Intel i9": {
        "BLAKE3":   [12.96, 250.53, 613.90, 500.30, 499.48, 495.43, 516.94, 522.63],
        "SHAKE128": [2.99, 69.34, 262.95, 218.73, 225.42, 233.51, 236.91, 235.54],
    },
    "AMD Ryzen 5": {
        "BLAKE3":   [16.02, 321.11, 810.92, 669.82, 686.78, 703.23, 751.40, 742.69],
        "SHAKE128": [2.72, 66.97, 296.27, 244.37, 262.08, 252.04, 283.54, 204.93],
    },
    "HP t630": {
        "BLAKE3":   [3.93, 92.94, 255.34, 217.73, 223.46, 211.84, 206.30, 203.88],
        "SHAKE128": [1.00, 23.57, 103.91, 80.83, 101.47, 71.50, 80.14, 90.61],
    },
}

labels = ['32B', '1KB', '64KB', '1MB', '2MB', '10MB', '50MB', '100MB']
x = np.arange(len(labels))

# Obliczenie stosunków BLAKE3 / SHAKE128
ratios = {}
for platform in throughput:
    blake3 = np.array(throughput[platform]["BLAKE3"])
    shake128 = np.array(throughput[platform]["SHAKE128"])
    ratios[platform] = blake3 / shake128

# Kolory platform
colors = {
    "Intel i9":    "#3182bd",  # niebieski
    "AMD Ryzen 5": "#74c476",  # zielony
    "HP t630":     "#e6550d",  # pomarańczowy/czerwony
}

markers = {
    "Intel i9":    "o",
    "AMD Ryzen 5": "s",
    "HP t630":     "^",
}

# ══════════════════════════════════════════════════════════════════════════
# RYSOWANIE WYKRESU
# ══════════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 6))

# Rysowanie linii dla każdej platformy
for platform in ["Intel i9", "AMD Ryzen 5", "HP t630"]:
    ax.plot(x, ratios[platform],
            color=colors[platform],
            marker=markers[platform],
            linewidth=2,
            markersize=7,
            label=platform,
            markerfacecolor=colors[platform],
            markeredgecolor='white',
            markeredgewidth=0.5)

# Linia referencyjna — parzystość (1x)
ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.7,
           label='Parzystość (1×)')

# Strefa typowego zakresu przewagi (2.5–3.5×)
ax.axhspan(2.5, 3.5, alpha=0.15, color='lightblue',
           label='Typowy zakres przewagi (2,5–3,5×)')

# Ustawienia osi
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel('Krotność przewagi BLAKE3 / SHAKE128', fontsize=11)
ax.set_xlabel('Rozmiar wyjścia XOF', fontsize=11)

# Zakres osi Y
ax.set_ylim(0, 12)
ax.set_yticks(np.arange(0, 13, 2))

# Tytuł
ax.set_title(
    'Rysunek 7.5. Stosunek przepustowości BLAKE3 do SHAKE128\n'
    'w funkcji rozmiaru wyjścia (trzy platformy)',
    fontsize=12, fontweight='bold', pad=15
)

# Siatka
ax.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Legenda
ax.legend(loc='upper right', fontsize=9, frameon=True, fancybox=True)

# Usunięcie górnej i prawej ramki
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig("Rys_7_5_stosunek_blake3_shake128.png", dpi=250, bbox_inches='tight')
plt.show()
print("Wykres zapisany!")
