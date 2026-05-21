#!/usr/bin/env python3
"""
Rysunek 7.2 — Przepustowość XOF — porównanie platform (wybrane rozmiary wyjścia)
Na podstawie Tabeli 7.2 (Turbo OFF)
"""

import matplotlib.pyplot as plt
import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# DANE Z TABELI 7.2 — wybrane rozmiary: 64 KB, 2 MB, 50 MB
# ══════════════════════════════════════════════════════════════════════════

# Format: {algorytm: {platforma: [64 KB, 2 MB, 50 MB]}}
data = {
    "BLAKE3": {
        "Intel i9":    [613.90, 499.48, 516.94],
        "AMD Ryzen 5": [810.92, 686.78, 751.40],
        "HP t630":     [255.34, 223.46, 206.30],
    },
    "SHAKE128": {
        "Intel i9":    [262.95, 225.42, 236.91],
        "AMD Ryzen 5": [296.27, 262.08, 283.54],
        "HP t630":     [103.91, 101.47, 80.14],
    },
    "SHAKE256": {
        "Intel i9":    [221.96, 194.39, 197.30],
        "AMD Ryzen 5": [239.36, 212.59, 218.72],
        "HP t630":     [89.64, 74.37, 72.16],
    },
}

labels = ['64 KB', '2 MB', '50 MB']
x = np.arange(len(labels))
width = 0.25

# Kolory platform — zgodne z oryginałem
colors_platform = {
    "Intel i9":    "#3182bd",  # niebieski
    "AMD Ryzen 5": "#74c476",  # zielony
    "HP t630":     "#e6550d",  # pomarańczowy/czerwony
}

# Kolory tytułów algorytmów
colors_algo = {
    "BLAKE3":   "#2196F3",  # niebieski
    "SHAKE128": "#E91E63",  # różowy
    "SHAKE256": "#FF9800",  # pomarańczowy
}

platforms = ["Intel i9", "AMD Ryzen 5", "HP t630"]

# ══════════════════════════════════════════════════════════════════════════
# RYSOWANIE WYKRESU
# ══════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(14, 5))

# Zakresy osi Y dla każdego algorytmu (zgodne z oryginałem)
y_limits = {
    "BLAKE3":   (0, 900),
    "SHAKE128": (0, 350),
    "SHAKE256": (0, 250),
}

y_ticks = {
    "BLAKE3":   np.arange(0, 901, 100),
    "SHAKE128": np.arange(0, 351, 50),
    "SHAKE256": np.arange(0, 251, 50),
}

for idx, (algo, ax) in enumerate(zip(["BLAKE3", "SHAKE128", "SHAKE256"], axes)):
    # Rysowanie słupków dla każdej platformy
    for p_idx, platform in enumerate(platforms):
        values = data[algo][platform]
        offset = (p_idx - 1) * width  # -width, 0, +width
        bars = ax.bar(x + offset, values, width,
                      label=platform,
                      color=colors_platform[platform],
                      edgecolor='white',
                      linewidth=0.5)
    
    # Tytuł algorytmu nad wykresem (kolorowy, pogrubiony)
    ax.set_title(algo, fontsize=13, fontweight='bold', 
                 color=colors_algo[algo], pad=15)
    
    # Oś X
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    
    # Oś Y — tylko dla pierwszego wykresu
    if idx == 0:
        ax.set_ylabel("MB/s", fontsize=11)
    
    # Zakres i ticki osi Y
    ax.set_ylim(y_limits[algo])
    ax.set_yticks(y_ticks[algo])
    
    # Siatka pozioma (subtelna)
    ax.grid(axis='y', linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Usunięcie górnej i prawej ramki
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Wspólna legenda na dole (pod środkowym wykresem)
axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
               ncol=3, fontsize=10, frameon=True, fancybox=True)

# Główny tytuł
fig.suptitle(
    "Rysunek 7.2. Przepustowość XOF — porównanie platform (wybrane rozmiary wyjścia)",
    fontsize=13, fontweight='bold', y=1.02
)

plt.tight_layout()
plt.savefig("Rys_7_2_porownanie_platform.png", dpi=250, bbox_inches='tight')
plt.show()
print("Wykres zapisany jako: Rys_7_2_porownanie_platform.png")
