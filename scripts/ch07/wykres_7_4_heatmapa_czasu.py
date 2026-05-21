#!/usr/bin/env python3
"""
Rysunek 7.4 — Czas wykonania jednej operacji XOF — heatmapa
(platforma × rozmiar wyjścia; kolor: skala log)
Na podstawie Tabeli 7.3 (Turbo OFF)
"""

import matplotlib.pyplot as plt
import numpy as np

# ══════════════════════════════════════════════════════════════════════════
# DANE Z TABELI 7.3
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
platforms = ["Intel i9", "AMD Ryzen 5", "HP t630"]

# Kolory tytułów algorytmów
colors_algo = {
    "BLAKE3":   "#2196F3",
    "SHAKE128": "#E91E63",
    "SHAKE256": "#FF9800",
}

# ══════════════════════════════════════════════════════════════════════════
# FUNKCJA FORMATUJĄCA WARTOŚCI CZASU
# ══════════════════════════════════════════════════════════════════════════

def format_time(val):
    """Formatuje wartość czasu do czytelnej postaci."""
    if val >= 1:
        return f"{val:.2f} s"
    elif val >= 0.1:
        return f"{val*1000:.1f} ms"
    elif val >= 0.001:
        return f"{val*1000:.2f} ms"
    elif val >= 0.0001:
        return f"{val*1000:.1f} ms"
    elif val >= 1e-5:
        return f"{val*1e6:.1f} µs"
    else:
        return f"{val*1e6:.1f} µs"

# ══════════════════════════════════════════════════════════════════════════
# RYSOWANIE WYKRESU
# ══════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, (algo, ax) in enumerate(zip(["BLAKE3", "SHAKE128", "SHAKE256"], axes)):
    # Przygotowanie danych do heatmapy: [platformy x rozmiary]
    heatmap_data = []
    for platform in platforms:
        heatmap_data.append(data_exec_time[platform][algo])
    
    heatmap_data = np.array(heatmap_data)
    
    # Logarytmiczna normalizacja dla lepszej wizualizacji
    heatmap_data_log = np.log10(heatmap_data)
    
    # Tworzenie heatmapy
    im = ax.imshow(heatmap_data_log, cmap='Blues', aspect='auto', 
                   interpolation='nearest')
    
    # Oś X — rozmiary wyjścia
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    
    # Oś Y — platformy
    ax.set_yticks(np.arange(len(platforms)))
    ax.set_yticklabels(platforms, fontsize=10)
    
    # Tytuł algorytmu
    ax.set_title(algo, fontsize=13, fontweight='bold', 
                 color=colors_algo[algo], pad=15)
    
    # Dodanie wartości liczbowych w komórkach
    for i in range(len(platforms)):
        for j in range(len(labels)):
            val = heatmap_data[i, j]
            text = format_time(val)
            
            # Kolor tekstu w zależności od jasności tła
            text_color = 'white' if heatmap_data_log[i, j] > np.max(heatmap_data_log) * 0.6 else 'black'
            
            ax.text(j, i, text, ha='center', va='center', 
                   fontsize=8, color=text_color, fontweight='bold')
    
    # Pasek kolorów (tylko dla ostatniego wykresu)
    if idx == 2:
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('log₁₀(czas [s])', fontsize=10)

# Główny tytuł
fig.suptitle(
    "Rysunek 7.4. Czas wykonania jednej operacji XOF — heatmapa\n"
    "(platforma × rozmiar wyjścia; kolor: skala log)",
    fontsize=13, fontweight='bold', y=1.02
)

plt.tight_layout()
plt.savefig("Rys_7_4_heatmapa_czasu.png", dpi=250, bbox_inches='tight')
plt.show()
