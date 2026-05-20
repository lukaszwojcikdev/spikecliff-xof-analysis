#!/usr/bin/env python3
"""
Rysunek 5.3 — Jednorodność geometryczna (grouped bar)
Skala 0–1; 1,0 = rozkład idealnie jednostajny.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Styl globalny ──────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'figure.dpi': 150,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

COLORS = {
    'BLAKE3':   '#2196F3',
    'SHAKE128': '#E91E63',
    'SHAKE256': '#FF9800',
}

# ══════════════════════════════════════════════════════════════════════════
# Rysunek 5.3 — Jednorodność geometryczna (grouped bar)
# ══════════════════════════════════════════════════════════════════════════
def plot_5_3(output='Rys_5_3_jednorodnosc.png'):
    """
    Jednorodność rozkładu punktów w R³ (wyniki z Tabel 5.3–5.5).
    Skala 0–1; 1,0 = rozkład idealnie jednostajny.
    """
    lengths_labels = ['2K bit', '8K bit', '64K bit', '1M bit', '16M bit']
    uniformity = {
        'SHAKE128': [0.91, 0.93, 0.95, 0.97, 0.98],
        'SHAKE256': [0.93, 0.94, 0.96, 0.98, 0.98],
        'BLAKE3':   [0.88, 0.90, 0.93, 0.96, 0.97],
    }
    
    x = np.arange(5)
    w = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    
    for i, alg in enumerate(['SHAKE128', 'SHAKE256', 'BLAKE3']):
        ax.bar(x + (i - 1) * w, uniformity[alg], w,
               label=alg, color=COLORS[alg],
               alpha=0.88, edgecolor='white')
    
    ax.axhline(1.0, color='black', linestyle='--',
               linewidth=1.2, alpha=0.5, label='Ideał = 1,0')
    ax.set_xticks(x)
    ax.set_xticklabels(lengths_labels)
    ax.set_xlabel('Długość strumienia')
    ax.set_ylabel('Jednorodność geometryczna')
    ax.set_ylim(0.82, 1.03)
    ax.legend()
    ax.set_title(
        'Rysunek 5.3. Jednorodność geometryczna rozkładu punktów w R³ '
        'w funkcji długości strumienia XOF',
        fontsize=10,
    )
    plt.tight_layout()
    fig.savefig(output, bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Zapisano: {output}')

# ══════════════════════════════════════════════════════════════════════════
# PUNKT WEJŚCIA
# ══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generowanie Rysunku 5.3')
    plot_5_3()
    print('Gotowe.')
