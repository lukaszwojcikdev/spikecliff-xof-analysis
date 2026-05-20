#!/usr/bin/env python3
"""
xof_4d_viz.py — Porównawcza wizualizacja projekcji 4D→3D dla XOF
=================================================================
Generuje cztery pliki PNG porównujące BLAKE3, SHAKE128 i SHAKE256
przy rozmiarach strumienia: 2048 bit, 8192 bit, 65 536 bit, 1 Mbit.

Bajty strumienia dzielone są na wektory 4D (co 4 bajty = 1 punkt),
normalizowane do [0, 1] i rzutowane perspektywicznie na 3D.
Kolor punktu = norma euklidesowa wektora 4D (colormap: plasma).

Użycie:
    python xof_4d_viz.py

Wymagania:
    pip install blake3 pycryptodomex matplotlib numpy

Wyjście:
    xof_4d_2048_bit.png
    xof_4d_8192_bit.png
    xof_4d_65_536_bit.png
    xof_4d_1_Mbit.png

"""

import numpy as np
import blake3
from Cryptodome.Hash import SHAKE128, SHAKE256
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Stałe ────────────────────────────────────────────────────────────────────
SEED    = b"xof_comparison_seed_2026"   # identyczne ziarno dla wszystkich algorytmów
W_DIST  = 2.0                           # odległość punktu projekcji (rzut perspektywiczny)
BG      = '#111111'                     # kolor tła (spójny z wiz1_1.py)
CMAP    = 'plasma'                      # colormap
DPI     = 150

# ── Generatory strumieni ──────────────────────────────────────────────────────
def gen_blake3(n_bytes: int) -> bytes:
    """BLAKE3 XOF — dowolna długość wyjścia."""
    return blake3.blake3(SEED).digest(length=n_bytes)

def gen_shake128(n_bytes: int) -> bytes:
    """SHAKE128 XOF."""
    return SHAKE128.new(SEED).read(n_bytes)

def gen_shake256(n_bytes: int) -> bytes:
    """SHAKE256 XOF."""
    return SHAKE256.new(SEED).read(n_bytes)

# ── Konwersja i rzut ──────────────────────────────────────────────────────────
def bytes_to_cloud(data: bytes, max_pts: int | None = None):
    """
    Konwertuje bajty na chmurę punktów 3D po rzucie perspektywicznym.

    Returns:
        pts   : (N, 3) float64 — współrzędne po rzucie
        norms : (N,)  float64 — normy wektorów 4D (kolor punktów)
    """
    arr = np.frombuffer(data, dtype=np.uint8)
    pad = (4 - len(arr) % 4) % 4
    if pad:
        arr = np.pad(arr, (0, pad))

    v4d = arr.reshape(-1, 4).astype(np.float64) / 255.0   # normalizacja do [0, 1]

    if max_pts and len(v4d) > max_pts:
        idx = np.random.choice(len(v4d), max_pts, replace=False)
        v4d = v4d[idx]

    # Rzut perspektywiczny 4D → 3D
    # xi' = xi * (D / (D - w)),  D = W_DIST
    w = W_DIST / (W_DIST - v4d[:, 3] + 1e-6)
    pts   = v4d[:, :3] * w[:, None]
    norms = np.linalg.norm(v4d, axis=1)
    return pts, norms

# ── Konfiguracja serii testowych ──────────────────────────────────────────────
SIZES = [
    (2048    // 8,   "2048 bit",    None),   # 256 B  — wszystkie punkty
    (8192    // 8,   "8192 bit",    None),   # 1 KB   — wszystkie punkty
    (65_536  // 8,   "65 536 bit",  None),   # 8 KB   — wszystkie punkty
    (1_000_000 // 8, "1 Mbit",      3000),   # 125 KB — subsample 3000 pkt
]

ALGOS = [
    ("BLAKE3",   gen_blake3),
    ("SHAKE128", gen_shake128),
    ("SHAKE256", gen_shake256),
]

# ── Główna pętla ──────────────────────────────────────────────────────────────
def main():
    np.random.seed(42)   # powtarzalność subsamplera

    for n_bytes, size_lbl, max_pts in SIZES:
        fig = plt.figure(figsize=(18, 6))
        fig.patch.set_facecolor(BG)
        fig.suptitle(
            f"GeoHash-Q / XOF — Projekcja 4D→3D  ·  {size_lbl}",
            color='white', fontsize=13, fontweight='bold', y=1.01
        )

        for col, (name, fn) in enumerate(ALGOS):
            ax = fig.add_subplot(1, 3, col + 1, projection='3d')
            ax.set_facecolor(BG)

            pts, norms = bytes_to_cloud(fn(n_bytes), max_pts=max_pts)

            sc = ax.scatter(
                pts[:, 0], pts[:, 1], pts[:, 2],
                c=norms, cmap=CMAP,
                s=35, alpha=0.8,
                edgecolors='k', linewidth=0.3
            )

            cbar = plt.colorbar(sc, ax=ax, shrink=0.55, pad=0.08)
            cbar.set_label('Norma punktu 4D', color='#aaaaaa', fontsize=8)
            cbar.ax.yaxis.set_tick_params(color='#aaaaaa', labelsize=7)
            plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#aaaaaa')

            ax.set_title(
                f"{name}  —  {size_lbl}\n{len(pts)} punktów",
                color='white', fontsize=10, fontweight='bold', pad=8
            )
            ax.set_xlabel('X', color='#aaaaaa', fontsize=8)
            ax.set_ylabel('Y', color='#aaaaaa', fontsize=8)
            ax.set_zlabel('Z', color='#aaaaaa', fontsize=8)
            ax.tick_params(colors='#888888', labelsize=6)

            for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
                pane.fill = False
                pane.set_edgecolor('#2a2a2a')
            ax.grid(True, color='#222222', linewidth=0.4)
            ax.view_init(elev=22, azim=45)

        plt.tight_layout()
        safe = size_lbl.replace(' ', '_').replace('/', '_')
        fname = f"xof_4d_{safe}.png"
        plt.savefig(fname, dpi=DPI, bbox_inches='tight', facecolor=BG)
        plt.close()
        print(f"Zapisano: {fname}")


if __name__ == "__main__":
    main()
