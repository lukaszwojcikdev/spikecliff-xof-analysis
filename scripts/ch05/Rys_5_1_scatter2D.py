#!/usr/bin/env python3
"""
Rysunek 5.1 — Scatter plot 2D (trzy panele)
Bajt(i) vs Bajt(i+1) znormalizowany do [0,1].
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
# GENERATOR STRUMIENI XOF
# ══════════════════════════════════════════════════════════════════════════
def gen_xof_bytes(alg: str, n_bytes: int, seed: bytes = b'xof_seed_2026') -> np.ndarray:
    """
    Generuje n_bytes bajtów przy użyciu wskazanego algorytmu XOF.
    """
    if alg == 'BLAKE3':
        import blake3
        return np.frombuffer(
            blake3.blake3(seed).digest(length=n_bytes),
            dtype=np.uint8,
        )
    elif alg == 'SHAKE128':
        from Crypto.Hash import SHAKE128
        h = SHAKE128.new()
        h.update(seed)
        return np.frombuffer(h.read(n_bytes), dtype=np.uint8)
    elif alg == 'SHAKE256':
        from Crypto.Hash import SHAKE256
        h = SHAKE256.new()
        h.update(seed)
        return np.frombuffer(h.read(n_bytes), dtype=np.uint8)
    else:
        raise ValueError(f'Nieznany algorytm: {alg}')

# ══════════════════════════════════════════════════════════════════════════
# Rysunek 5.1 — Scatter 2D, trzy panele
# ══════════════════════════════════════════════════════════════════════════
def plot_5_1(output='Rys_5_1_scatter2D.png'):
    """
    Bajt(i) vs Bajt(i+1) znormalizowany do [0,1].
    n_pts = 8192 punktów = 16 384 bajtów strumienia.
    Siatka 8×8 wizualizuje test jednorodności.
    """
    n_pts = 8192
    algs  = ['SHAKE128', 'SHAKE256', 'BLAKE3']
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    
    for ax, alg in zip(axes, algs):
        data = gen_xof_bytes(alg, n_pts * 2)
        x = data[:n_pts]  / 255.0
        y = data[n_pts:]  / 255.0
        
        ax.scatter(x, y, s=0.8, alpha=0.4,
                   c=COLORS[alg], rasterized=True)
        ax.set_title(alg, fontsize=11,
                     color=COLORS[alg], fontweight='bold')
        ax.set_xlabel('Bajt i / 255')
        ax.set_ylabel('Bajt i+1 / 255' if ax is axes[0] else '')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        
        # Siatka 8×8 jako wizualny grid test
        for tick in np.linspace(0, 1, 9):
            ax.axhline(tick, color='gray', lw=0.3, alpha=0.4)
            ax.axvline(tick, color='gray', lw=0.3, alpha=0.4)
    
    fig.suptitle(
        'Rysunek 5.1. Scatter plot 2D strumieni XOF — bajt(i) vs bajt(i+1) '
        '(64 KB, 8 bitów/współrzędna; siatka 8×8 dla oceny jednorodności)',
        fontsize=10, y=1.02,
    )
    plt.tight_layout()
    fig.savefig(output, bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Zapisano: {output}')

# ══════════════════════════════════════════════════════════════════════════
# PUNKT WEJŚCIA
# ══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generowanie Rysunku 5.1')
    plot_5_1()
    print('Gotowe.')
