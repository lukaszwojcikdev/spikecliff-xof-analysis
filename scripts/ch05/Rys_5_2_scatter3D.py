#!/usr/bin/env python3
"""
Rysunek 5.2 — Scatter plot 3D (trzy panele)
Bajt(i), bajt(i+1), bajt(i+2) → punkt w R³.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — rejestruje projekcję 3D

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
# Rysunek 5.2 — Scatter 3D, trzy panele
# ══════════════════════════════════════════════════════════════════════════
def plot_5_2(output='Rys_5_2_scatter3D.png'):
    """
    Bajt(i), bajt(i+1), bajt(i+2) → punkt w R³.
    n_pts = 4096 punktów; kolor = norma euklidesowa wektora.
    """
    n_pts = 4096
    algs  = ['SHAKE128', 'SHAKE256', 'BLAKE3']
    fig = plt.figure(figsize=(14, 5))
    
    for idx, alg in enumerate(algs):
        ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
        data = gen_xof_bytes(alg, n_pts * 3)
        x = data[:n_pts]          / 255.0
        y = data[n_pts:2*n_pts]   / 255.0
        z = data[2*n_pts:3*n_pts] / 255.0
        norms = np.sqrt(x**2 + y**2 + z**2)
        
        ax.scatter(x, y, z,
                   c=norms, cmap='plasma', s=1.5,
                   alpha=0.5, rasterized=True)
        ax.set_title(alg, color=COLORS[alg],
                     fontweight='bold', fontsize=10, pad=4)
        ax.set_xlabel('X', fontsize=7, labelpad=0)
        ax.set_ylabel('Y', fontsize=7, labelpad=0)
        ax.set_zlabel('Z', fontsize=7, labelpad=0)
        ax.tick_params(labelsize=6)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_zlim(0, 1)
        ax.view_init(elev=22, azim=45)
    
    fig.suptitle(
        'Rysunek 5.2. Projekcja 3D strumieni XOF — bajt(i), bajt(i+1), bajt(i+2) '
        '(4096 punktów; kolor = norma euklidesowa)',
        fontsize=10, y=1.0,
    )
    plt.tight_layout()
    fig.savefig(output, bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Zapisano: {output}')

# ══════════════════════════════════════════════════════════════════════════
# PUNKT WEJŚCIA
# ══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generowanie Rysunku 5.2')
    plot_5_2()
    print('Gotowe.')
