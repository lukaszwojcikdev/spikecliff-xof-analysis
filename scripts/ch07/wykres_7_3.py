#!/usr/bin/env python3
"""
Rysunek 7.3 — Czas wykonania XOF [s] w skali log-log, trzy platformy
Na podstawie Tabeli 7.3 (Turbo OFF)
"""

import matplotlib.pyplot as plt
import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# DANE Z TABELI 7.3 — Czas wykonania [s] jednej operacji XOF, Turbo OFF
# ══════════════════════════════════════════════════════════════════════════

data_exec_time = {
    "Intel i9": {
        "BLAKE3":   [2.00e-6, 4.00e-6, 1.07e-4, 2.096e-3, 4.199e-3, 2.117e-2, 1.014e-1, 2.006e-1],
        "SHAKE128": [1.10e-5, 1.50e-5, 2.49e-4, 4.794e-3, 9.303e-3, 4.491e-2, 2.213e-1, 4.452e-1],
        "SHAKE256": [1.10e-5, 1.60e-5, 2.95e-4, 5.527e-3, 1.079e-2, 5.295e-2, 2.657e-1, 5.208e-1],
    },
    "AMD Ryzen 5": {
        "BLAKE3":   [2.00e-6, 3.00e-6, 8.10e-5, 1.565e-3, 3.054e-3, 1.491e-2, 6.978e-2, 1.412e-1],
        "SHAKE128": [1.20e-5, 1.50e-5, 2.21e-4, 4.291e-3, 8.002e-3, 4.160e-2, 1.849e-1, 5.117e-1],
        "SHAKE256": [1.40e-5, 1.60e-5, 2.74e-4, 5.262e-3, 9.865e-3, 4.712e-2, 2.397e-1, 5.430e-1],
    },
    "HP t630": {
        "BLAKE3":   [8.00e-6, 1.10e-5, 2.57e-4, 4.816e-3, 9.385e-3, 4.950e-2, 2.541e-1, 5.143e-1],
        "SHAKE128": [3.20e-5, 4.30e-5, 6.31e-4, 1.297e-2, 2.067e-2, 1.467e-1, 6.542e-1, 1.157e+0],
        "SHAKE256": [3.80e-5, 4.70e-5, 7.31e-4, 1.168e-2, 2.820e-2, 1.339e-1, 7.266e-1, 1.570e+0],
    },
}

labels = ['32 B', '1 KB', '64 KB', '1 MB', '2 MB', '10 MB', '50 MB', '100 MB']
x = np.arange(len(labels))

# Kolory algorytmów
colors_algo = {
    "BLAKE3":   "#2196F3",  # niebieski
    "SHAKE128": "#E91E63",  # różowy
    "SHAKE256": "#FF9800",  # pomarańczowy
}

markers = {
    "BLAKE3":   "o",
    "SHAKE128": "s",
    "SHAKE256": "^",
}

platforms = ["Intel i9", "AMD Ryzen 5", "HP t630"]

# ══════════════════════════════════════════════════════════════════════════
# RYSOWANIE WYKRESU
# ══════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

for idx, (platform, ax) in enumerate(zip(platforms, axes)):
    for algo in ["BLAKE3", "SHAKE128", "SHAKE256"]:
        values = data_exec_time[platform][algo]
        ax.plot(x, values,
                color=colors_algo[algo],
                marker=markers[algo],
                linewidth=2,
                markersize=6,
                label=algo,
                markerfacecolor=colors_algo[algo],
                markeredgecolor='white',
                markeredgewidth=0.5)
    
    # Skala logarytmiczna na obu osiach
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    # Tytuł platformy
    ax.set_title(platform, fontsize=12, fontweight='bold', pad=10)
    
    # Oś X
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    
    # Oś Y — tylko dla pierwszego wykresu
    if idx == 0:
        ax.set_ylabel("Czas [s]", fontsize=11)
    
    # Zakres osi Y
    ax.set_ylim(1e-6, 2e0)
    
    # Siatka
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    
    # Usunięcie górnej i prawej ramki
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Wspólna legenda
axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.22),
               ncol=3, fontsize=10, frameon=True, fancybox=True)

# Główny tytuł
fig.suptitle(
    "Rysunek 7.3. Czas wykonania XOF [s] — skala log-log, trzy platformy",
    fontsize=13, fontweight='bold', y=1.02
)

plt.tight_layout()
plt.savefig("Rys_7_3_czas_wykonania_loglog.png", dpi=250, bbox_inches='tight')
plt.show()
