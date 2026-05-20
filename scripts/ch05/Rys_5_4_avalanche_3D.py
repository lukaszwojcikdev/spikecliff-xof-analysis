#!/usr/bin/env python3
"""
Rysunek 5.4 — Efekt lawinowy geometrycznie (centroidy w 3D)
Dwie chmury punktów (ziarna A i B różniące się 1 bajtem) w R³.
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
# Rysunek 5.4 — Efekt lawinowy geometrycznie (centroidy w R³)
# ══════════════════════════════════════════════════════════════════════════
def plot_5_4(output='Rys_5_4_avalanche_3D.png'):
    """
    Dwie chmury punktów (ziarna A i B różniące się 1 bajtem) w R³.
    Strzałki pokazują przesunięcie centroidu po zmianie ziarna.
    Małe przesunięcie (losowe) dowodzi braku strukturalnej asymetrii.
    """
    n_pts  = 1024
    seed_a = b'avalanche_seed_A_2026'
    seed_b = b'avalanche_seed_B_2026'  # różni się jednym bajtem (B→B)
    algs   = ['SHAKE128', 'SHAKE256', 'BLAKE3']
    fig = plt.figure(figsize=(13, 5))
    
    for idx, alg in enumerate(algs):
        ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
        da = gen_xof_bytes(alg, n_pts * 3, seed=seed_a)
        db = gen_xof_bytes(alg, n_pts * 3, seed=seed_b)
        
        xa = da[:n_pts]          / 255.0
        ya = da[n_pts:2*n_pts]   / 255.0
        za = da[2*n_pts:3*n_pts] / 255.0
        xb = db[:n_pts]          / 255.0
        yb = db[n_pts:2*n_pts]   / 255.0
        zb = db[2*n_pts:3*n_pts] / 255.0
        
        # Chmury punktów (rzadkie, przezroczyste)
        ax.scatter(xa, ya, za, s=1, alpha=0.18,
                   c=COLORS[alg], rasterized=True, label='Ziarno A')
        ax.scatter(xb, yb, zb, s=1, alpha=0.18,
                   c='#90A4AE', rasterized=True, label='Ziarno B')
        
        # Centroidy
        cx_a, cy_a, cz_a = xa.mean(), ya.mean(), za.mean()
        cx_b, cy_b, cz_b = xb.mean(), yb.mean(), zb.mean()
        
        ax.scatter([cx_a], [cy_a], [cz_a], s=80,
                   c=COLORS[alg], marker='*', zorder=5)
        ax.scatter([cx_b], [cy_b], [cz_b], s=80,
                   c='black', marker='^', zorder=5)
        
        # Strzałka przesunięcia centroidu
        ax.quiver(cx_a, cy_a, cz_a,
                  cx_b - cx_a, cy_b - cy_a, cz_b - cz_a,
                  color='red', arrow_length_ratio=0.35, linewidth=1.5)
        
        dist = np.sqrt((cx_b-cx_a)**2 + (cy_b-cy_a)**2 + (cz_b-cz_a)**2)
        ax.set_title(
            f'{alg}\nΔ centroid = {dist:.4f}',
            color=COLORS[alg], fontweight='bold', fontsize=9,
        )
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_zlim(0, 1)
        ax.tick_params(labelsize=6)
        ax.view_init(elev=25, azim=50)
    
    fig.suptitle(
        'Rysunek 5.4. Efekt lawinowy geometrycznie — przesunięcie centroidu '
        'przy minimalnej zmianie ziarna wejściowego (n = 1024 punktów w R³)',
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
    print('Generowanie Rysunku 5.4')
    plot_5_4()
    print('Gotowe.')
