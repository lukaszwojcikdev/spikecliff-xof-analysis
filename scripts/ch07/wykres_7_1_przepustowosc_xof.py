#!/usr/bin/env python3
"""
Rysunek 7.1 — Przepustowość XOF [MB/s] w funkcji rozmiaru wyjścia
(Turbo OFF; skala logarytmiczna)

Na podstawie Tabeli 7.2
"""

import matplotlib.pyplot as plt
import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# DANE Z TABELI 7.2 — Przepustowość XOF [MB/s], Turbo OFF, mediana
# ══════════════════════════════════════════════════════════════════════════

data = {
    "Intel i9": {
        "BLAKE3":    [12.96, 250.53, 613.90, 500.30, 499.48, 495.43, 516.94, 522.63],
        "SHAKE128":  [2.99, 69.34, 262.95, 218.73, 225.42, 233.51, 236.91, 235.54],
        "SHAKE256":  [2.86, 64.84, 221.96, 189.74, 194.39, 198.02, 197.30, 201.35],
    },
    "AMD Ryzen 5": {
        "BLAKE3":    [16.02, 321.11, 810.92, 669.82, 686.78, 703.23, 751.40, 742.69],
        "SHAKE128":  [2.72, 66.97, 296.27, 244.37, 262.08, 252.04, 283.54, 204.93],
        "SHAKE256":  [2.27, 64.32, 239.36, 199.27, 212.59, 222.55, 218.72, 193.11],
    },
    "HP t630": {
        "BLAKE3":    [3.93, 92.94, 255.34, 217.73, 223.46, 211.84, 206.30, 203.88],
        "SHAKE128":  [1.00, 23.57, 103.91, 80.83, 101.47, 71.50, 80.14, 90.61],
        "SHAKE256":  [0.83, 21.75, 89.64, 89.77, 74.37, 78.30, 72.16, 66.77],
    },
}

labels = ['32 B', '1 KB', '64 KB', '1 MB', '2 MB', '10 MB', '50 MB', '100 MB']
x = np.arange(len(labels))

# Kolory zgodne z oryginałem
colors = {
    "BLAKE3":   "#2196F3",   # niebieski
    "SHAKE128": "#E91E63",   # różowy/magenta
    "SHAKE256": "#FF9800",   # pomarańczowy
}

markers = {
    "BLAKE3":   "o",
    "SHAKE128": "s",
    "SHAKE256": "^",
}

# ══════════════════════════════════════════════════════════════════════════
# RYSOWANIE WYKRESU
# ══════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

platform_titles = ["Intel i9", "AMD Ryzen 5", "HP t630"]

for idx, (platform, ax) in enumerate(zip(platform_titles, axes)):
    for algo in ["BLAKE3", "SHAKE128", "SHAKE256"]:
        values = data[platform][algo]
        ax.plot(x, values,
                color=colors[algo],
                marker=markers[algo],
                linewidth=2,
                markersize=6,
                label=algo,
                markerfacecolor=colors[algo],
                markeredgecolor='white',
                markeredgewidth=0.5)

    # Skala logarytmiczna na osi Y
    ax.set_yscale('log')

    # Zakresy osi Y — dostosowane do platformy
    if platform in ["Intel i9", "AMD Ryzen 5"]:
        ax.set_ylim(1, 1500)
        ax.set_yticks([1, 10, 100, 1000])
        ax.set_yticklabels(['1', '10', '100', '1000'])
    else:  # HP t630
        ax.set_ylim(0.5, 500)
        ax.set_yticks([1, 10, 100])
        ax.set_yticklabels(['1', '10', '100'])

    # Tytuł podwykresu
    ax.set_title(platform, fontsize=12, fontweight='bold', pad=10)

    # Oś X
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)

    # Oś Y — tylko dla pierwszego wykresu
    if idx == 0:
        ax.set_ylabel("Przepustowość [MB/s]", fontsize=11)

    # Siatka
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)

    # Wspólna legenda poniżej środkowego wykresu
    if idx == 1:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22),
                  ncol=3, fontsize=10, frameon=True, fancybox=True)

# Główny tytuł
fig.suptitle(
    "Rysunek 7.1. Przepustowość XOF [MB/s] w funkcji rozmiaru wyjścia\n"
    "(Turbo OFF; skala logarytmiczna)",
    fontsize=13, fontweight='bold', y=1.02
)

plt.tight_layout()
plt.savefig("Rys_7_1_przepustowosc_xof.png", dpi=250, bbox_inches='tight')
plt.show()
print("Wykres zapisany jako: Rys_7_1_przepustowosc_xof.png")
