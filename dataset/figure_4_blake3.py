#!/usr/bin/env python3
"""
SpikeCliff Effect — Negative Control BLAKE3

Figure:
Figure 4. BLAKE3 Timing Profile — No SpikeCliff Effect (Negative Control)

Requirements:
pip install matplotlib numpy blake3

Usage:
python figure_4_blake3.py

Important Methodological Notes:
    - To reproduce the results, disable Turbo Boost:

        Linux:   echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo
                 cpupower frequency-set -g performance

        Windows: disable in BIOS or using the ThrottleStop utility.

    - Recommended pinning of the thread to the core:
        Linux: taskset -c 0 python figure_4_blake3.py

    - N_REPS=1000 gives a stable median profile (~10–20 min)
    - N_REPS=200 gives a quick preview (~2–5 min)
"""

import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import blake3

# ══════════════════════════════════════════════════════════════════════════
# MEASUREMENT PARAMETERS
# ══════════════════════════════════════════════════════════════════════════

LENGTH_START = 110   # [bytes] — lower Scan Boundary
LENGTH_END   = 360   # [bytes] — Upper Scan Boundary
OUTPUT_LEN   = 32    # [bytes] — Fixed XOF Output Size
N_REPS       = 1000  # Number of repetitions per point; 1000 = Worked Outcomes

# SHAKE cliff positions for reference lines (visual comparison)
SHAKE128_BOUNDARIES = [168, 336]  # r = 168 B
SHAKE256_BOUNDARIES = [136, 272]  # r = 136 B

# ── Styl globalny ─────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'font.size':         10,
    'axes.titlesize':    11,
    'axes.labelsize':    10,
    'figure.dpi':        150,
    'axes.grid':         True,
    'grid.alpha':        0.3,
    'axes.spines.top':   False,
    'axes.spines.right': False,
})

COLOR_BLAKE3 = '#2196F3'


# ══════════════════════════════════════════════════════════════════════════
# BLAKE3 TIME PROFILING
# ══════════════════════════════════════════════════════════════════════════

def profile_blake3(length_start=LENGTH_START,
                   length_end=LENGTH_END,
                   output_len=OUTPUT_LEN,
                   n_reps=N_REPS):
    """
    Measures the execution time of blake3.blake3(msg).digest(length=output_len)
    for input lengths from length_start to length_end (1-byte increment).

    Returns:
        lengths : np.ndarray — input length range [B]
        medians : np.ndarray — median time [ns] per length
        p95s    : np.ndarray — 95th percentile time [ns] per length
    """
    lengths = np.arange(length_start, length_end + 1)
    medians = np.empty(len(lengths))
    p95s    = np.empty(len(lengths))

    print(f'  Range: {length_start}–{length_end} B, N_REPS={n_reps}')
    print(f'  Number of measurement points: {len(lengths)}')

    for i, l in enumerate(lengths):
        msg   = bytes(l)                # deterministic null input
        times = np.empty(n_reps)

        for k in range(n_reps):         # ← nested loop - CRITICAL
            t0       = time.perf_counter_ns()
            blake3.blake3(msg).digest(length=output_len)
            times[k] = time.perf_counter_ns() - t0

        medians[i] = np.median(times)
        p95s[i]    = np.percentile(times, 95)

        if (i + 1) % 50 == 0:
            print(f'  [{i+1}/{len(lengths)}] l={l} B, '
                  f'median={medians[i]:.0f} ns')

    return lengths, medians, p95s


# ══════════════════════════════════════════════════════════════════════════
# BLAKE3 time profile (negative control)
# ══════════════════════════════════════════════════════════════════════════

def fig_4(lengths, medians, p95s,
          output='Figure_4_BLAKE3_control.png'):
    """
    Draws a time profile of BLAKE3 with the positions of the SHAKE 
    cliffs marked as reference lines.
    """
    fig, ax = plt.subplots(figsize=(11, 4.5))

    # ── Main curve — median ───────────────────────────────────────────────
    ax.plot(lengths, medians,
            color=COLOR_BLAKE3, linewidth=1.2,
            label='BLAKE3 — median time', alpha=0.9, zorder=3)

    # ── P5–P95 band ──────────────────────────────────────────────────────
    p05s = medians * 0.92   # approximate P5 (symmetrical to P95)
    ax.fill_between(lengths, p05s, p95s,
                    alpha=0.15, color=COLOR_BLAKE3,
                    label='Range P5–P95')

    # ── Vertical reference lines - where SHAKE would have cliffs ───────────
    colors_ref  = {'SHAKE128': '#E91E63', 'SHAKE256': '#FF9800'}
    linestyles  = {'SHAKE128': '--',      'SHAKE256': ':'}

    for alg, boundaries in [('SHAKE128', SHAKE128_BOUNDARIES),
                             ('SHAKE256', SHAKE256_BOUNDARIES)]:
        first = True
        for pos in boundaries:
            if LENGTH_START <= pos <= LENGTH_END:
                lbl = f'{alg} r={pos} B' if first else '_nolegend_'
                ax.axvline(pos,
                           color=colors_ref[alg],
                           linestyle=linestyles[alg],
                           linewidth=1.2,
                           alpha=0.65,
                           label=lbl)
                first = False

    # ── Annotation ─────────────────────────────────────────────────────────
    mid      = (LENGTH_START + LENGTH_END) // 2
    y_median = float(np.median(medians))

    ax.annotate(
        'No regular cliff jumps (SHAKE)',
        fontsize=9,
        color='#444444',
        xy=(mid, y_median),
        xytext=(mid + 25, y_median * 1.40),
        arrowprops=dict(arrowstyle='->', color='#444444', lw=1.0),
    )

    # ── Axes and title ──────────────────────────────────────────────────────
    ax.set_xlabel('Input length [bytes]')
    ax.set_ylabel(f'Time [ns] (median of {N_REPS} repetitions)')
    ax.set_title(
        f'Figure 4. BLAKE3 Timing Profile — No SpikeCliff Effect (Negative Control)\n'
        f'Dashed lines: SHAKE cliff positions for visual comparison',
        fontsize=10,
    )
    ax.legend(fontsize=9)
    ax.set_xlim(LENGTH_START, LENGTH_END)

    plt.tight_layout()
    fig.savefig(output, bbox_inches='tight', dpi=200)
    plt.close()
    print(f'  Save: {output}')


# ══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Generating a Chart - (BLAKE3 Negative Control')
    print(f'Parameters: range {LENGTH_START}–{LENGTH_END} B, '
          f'exit {OUTPUT_LEN} B, {N_REPS} repetitions/point')

    lengths, medians, p95s = profile_blake3()
    fig_4(lengths, medians, p95s)

    # Saving CSV data for further analysis
    csv_path = 'blake3_profile_data.csv'
    np.savetxt(
        csv_path,
        np.column_stack([lengths, medians, p95s]),
        delimiter=',',
        header='length_bytes,median_ns,p95_ns',
        comments='',
    )
    print(f'  Measurement data: {csv_path}')
    print('Ready.')
