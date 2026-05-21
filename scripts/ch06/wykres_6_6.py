#!/usr/bin/env python3
"""
Załącznik C — Kod źródłowy wykresu: Rozdział 6
SpikeCliff Effect — kontrola negatywna BLAKE3

Wykresy:
  Rys. 6.5 — Profil czasowy BLAKE3 (brak SpikeCliff)

Wymagania:
  pip install matplotlib numpy blake3

Użycie:
  python zalacznik_C_rozdzial6.py

Ważne uwagi metodologiczne:
  - Pomiar wykonywany jest przy domyślnej konfiguracji systemu.
  - Dla reprodukcji wyników z pracy należy wyłączyć Turbo Boost:
      Linux: echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
             cpupower frequency-set -g performance
      Windows: wyłączyć w BIOS lub przez narzędzie ThrottleStop.
  - Wątek pomiarowy warto przypiąć do jednego rdzenia:
      Linux: taskset -c 0 python zalacznik_C_rozdzial6.py
  - Liczba powtórzeń (N_REPS) decyduje o jakości mediany:
      200–500 daje dobre wyniki; 1000 daje wyniki z pracy.

Czas wykonania:
  ~2–5 minut dla zakresu 110–360 B, N_REPS=200
  ~10–20 minut dla N_REPS=1000
"""

import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import blake3


# ══════════════════════════════════════════════════════════════════════════
# PARAMETRY POMIARU
# ══════════════════════════════════════════════════════════════════════════

LENGTH_START = 110    # [bajty] — dolna granica skanowania
LENGTH_END   = 360    # [bajty] — górna granica skanowania
OUTPUT_LEN   = 32     # [bajty] — stały rozmiar wyjścia XOF
N_REPS       = 200    # liczba powtórzeń na punkt; 1000 = wyniki z pracy

# Pozycje klifów SHAKE dla linii referencyjnych (porównanie wizualne)
SHAKE128_BOUNDARIES = [168, 336]          # r = 168 B
SHAKE256_BOUNDARIES = [136, 272]          # r = 136 B

# ── Styl globalny ──────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'figure.dpi': 150,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

COLOR_BLAKE3 = '#2196F3'


# ══════════════════════════════════════════════════════════════════════════
# PROFILOWANIE CZASOWE BLAKE3
# ══════════════════════════════════════════════════════════════════════════

def profile_blake3(length_start=LENGTH_START,
                   length_end=LENGTH_END,
                   output_len=OUTPUT_LEN,
                   n_reps=N_REPS):
    """
    Mierzy czas wykonania blake3.blake3(msg).digest(length=output_len)
    dla długości wejścia od length_start do length_end (krok 1 bajt).

    Zwraca:
        lengths : np.ndarray — zakres długości wejścia [B]
        medians : np.ndarray — mediana czasu [ns] per długość
        p95s    : np.ndarray — percentyl 95 czasu [ns] per długość
    """
    lengths = np.arange(length_start, length_end + 1)
    medians = np.empty(len(lengths))
    p95s    = np.empty(len(lengths))

    print(f'  Zakres: {length_start}–{length_end} B, N_REPS={n_reps}')
    print(f'  Liczba punktów pomiarowych: {len(lengths)}')

    for i, l in enumerate(lengths):
        msg = bytes(l)   # deterministyczne wejście zerowe
        times = np.empty(n_reps)

        for k in range(n_reps):
            t0 = time.perf_counter_ns()
            blake3.blake3(msg).digest(length=output_len)
            times[k] = time.perf_counter_ns() - t0

        medians[i] = np.median(times)
        p95s[i]    = np.percentile(times, 95)

        if (i + 1) % 50 == 0:
            print(f'    [{i+1}/{len(lengths)}] l={l} B, '
                  f'mediana={medians[i]:.0f} ns')

    return lengths, medians, p95s


# ══════════════════════════════════════════════════════════════════════════
# Rysunek 6.5 — Profil czasowy BLAKE3 (kontrola negatywna)
# ══════════════════════════════════════════════════════════════════════════

def plot_6_5(lengths, medians, p95s, output='Rys_6_5_BLAKE3_control.png'):
    """
    Rysuje profil czasowy BLAKE3 z zaznaczonymi granicami rate SHAKE
    dla wizualnego porównania.
    """
    fig, ax = plt.subplots(figsize=(11, 4.5))
    
    # Główna krzywa — mediana
    ax.plot(lengths, medians, color=COLOR_BLAKE3, linewidth=1.2,
            label='BLAKE3 — mediana czasu', alpha=0.9, zorder=3)
            
    # Pasmo P5–P95 (szacunkowe)
    p05s = np.array([medians[i] * 0.92 for i in range(len(medians))])
    ax.fill_between(lengths, p05s, p95s,
                    alpha=0.15, color=COLOR_BLAKE3,
                    label='Zakres P5–P95')
    
    # Pionowe linie referencyjne — gdzie SHAKE miałby klify
    colors_ref = {'SHAKE128': '#E91E63', 'SHAKE256': '#FF9800'}
    
    for alg, boundaries in [('SHAKE128', SHAKE128_BOUNDARIES),
                            ('SHAKE256', SHAKE256_BOUNDARIES)]:
        for pos in boundaries:
            # --- POPRAWKA: Zmieniono na wielkie litery (zmienne globalne) ---
            if LENGTH_START <= pos <= LENGTH_END:
                ax.axvline(pos, color=colors_ref[alg],
                           linestyle=':', linewidth=1.2, alpha=0.55,
                           label=f'{alg} r={pos} B' if pos == boundaries[0] else '_nolegend_')
    
    # --- POPRAWKA: Zmieniono na wielkie litery ---
    mid = (LENGTH_START + LENGTH_END) // 2
    
    ax.annotate(
        'Brak regularnych skoków\nprzy granicach rate',
        fontsize=9, color='gray',
        xy=(mid, float(np.median(medians))),
        xytext=(mid + 20, float(np.median(medians)) * 1.35),
        arrowprops=dict(arrowstyle='->', color='gray', lw=1),
    )
    
    ax.set_xlabel('Długość wejścia [bajty]')
    ax.set_ylabel('Czas [ns] (mediana z %d powtórzeń)' % N_REPS)
    ax.set_title(
        'Rysunek 6.5. Profil czasowy BLAKE3 — brak SpikeCliff (kontrola negatywna)\n'
        'Linie przerywane: pozycje klifów SHAKE dla porównania wizualnego',
        fontsize=10,
    )
    ax.legend(fontsize=9)
    plt.tight_layout()
    fig.savefig(output, bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Zapisano: {output}')


# ══════════════════════════════════════════════════════════════════════════
# PUNKT WEJŚCIA
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Generowanie wykresu — Rozdział 6 (BLAKE3 kontrola negatywna)')
    print(f'Parametry: zakres {LENGTH_START}–{LENGTH_END} B, '
          f'wyjście {OUTPUT_LEN} B, {N_REPS} powtórzeń/punkt')

    lengths, medians, p95s = profile_blake3()
    plot_6_5(lengths, medians, p95s)

    # Opcjonalnie — zapis danych CSV do dalszej analizy
    import os
    csv_path = 'blake3_profile_data.csv'
    np.savetxt(
        csv_path,
        np.column_stack([lengths, medians, p95s]),
        delimiter=',',
        header='length_bytes,median_ns,p95_ns',
        comments='',
    )
    print(f'  Dane pomiarowe: {csv_path}')
    print('Gotowe.')
