#!/usr/bin/env python3
"""
scripts/ch07/throughput_sweep.py
----------------------------------
Benchmark przepustowości XOF dla zakresu 32 B – 100 MB wyjścia.
Odpowiada skryptowi throughput_v4_czas.py z §7.1 pracy.

Użycie
------
  # Podstawowy pomiar (Intel i9 / Ryzen — Windows CMD lub WSL2)
  python scripts/ch07/throughput_sweep.py

  # Z pinowaniem rdzenia (HP t630 / Linux Mint)
  taskset -c 0 python3 scripts/ch07/throughput_sweep.py

  # Pełny zakres, wszystkie algorytmy
  python scripts/ch07/throughput_sweep.py \\
      --xofs blake3 shake128 shake256 \\
      --sizes 32 1024 65536 1048576 2097152 10485760 52428800 104857600 \\
      --output data/raw/ch07_throughput/sweep_$(hostname).csv

  # Tylko BLAKE3, szybki test
  python scripts/ch07/throughput_sweep.py --xofs blake3 --min-time 0.5
"""

import argparse
import csv
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'src'))

from xof_generators import hash_message, SUPPORTED

# Rozmiary wyjścia z §7.1 pracy [bajty]
DEFAULT_SIZES = [
    32,          # typowy hash jednorazowy
    1024,        # 1 KB
    65536,       # 64 KB — szczyt throughput BLAKE3
    1048576,     # 1 MB
    2097152,     # 2 MB
    10485760,    # 10 MB
    52428800,    # 50 MB
    104857600,   # 100 MB
]

INPUT_MSG_SIZE = 1024  # 1 KB wejście — stałe (jak w §7.1)


def measure_throughput(
    alg: str,
    output_len: int,
    min_time_s: float = 1.0,
    warmup_iters: int = 100,
) -> dict:
    """
    Mierzy przepustowość XOF dla danego rozmiaru wyjścia.

    Automatycznie dobiera liczbę iteracji tak, by łączny czas pomiaru
    przekraczał min_time_s (zgodnie z §7.1 pracy).

    Zwraca
    ------
    dict: throughput_mbs, time_per_call_s, n_iters, output_bytes
    """
    msg = os.urandom(INPUT_MSG_SIZE)

    # Warm-up
    for _ in range(warmup_iters):
        hash_message(alg, msg, output_len)

    # Kalibracja liczby iteracji
    t0      = time.perf_counter()
    n_probe = 10
    for _ in range(n_probe):
        hash_message(alg, msg, output_len)
    t_probe  = time.perf_counter() - t0
    t_single = t_probe / n_probe

    n_iters = max(10, int(min_time_s / t_single) + 1)
    if output_len >= 10_000_000:  # ≥ 10 MB — minimum 2 sekundy
        n_iters = max(n_iters, int(2.0 / t_single) + 1)

    # Właściwy pomiar
    t_start = time.perf_counter()
    for _ in range(n_iters):
        hash_message(alg, msg, output_len)
    t_total = time.perf_counter() - t_start

    t_per_call   = t_total / n_iters
    total_bytes  = output_len * n_iters
    throughput   = total_bytes / t_total / 1_048_576  # MB/s

    return {
        'throughput_mbs':   round(throughput, 2),
        'time_per_call_s':  t_per_call,
        'n_iters':          n_iters,
        'total_time_s':     t_total,
        'output_bytes':     output_len,
    }


def size_label(n: int) -> str:
    """Czytelna etykieta rozmiaru."""
    if n < 1024:            return f'{n} B'
    elif n < 1048576:       return f'{n//1024} KB'
    elif n < 1073741824:    return f'{n//1048576} MB'
    else:                   return f'{n//1073741824} GB'


def parse_args():
    p = argparse.ArgumentParser(
        description='Benchmark przepustowości XOF (throughput_v4_czas.py)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument('--xofs', nargs='+', default=list(SUPPORTED))
    p.add_argument('--sizes', nargs='+', type=int, default=DEFAULT_SIZES,
                   help='Rozmiary wyjścia [bajty]')
    p.add_argument('--min-time', type=float, default=1.0,
                   help='Minimalny czas pomiaru per punkt [s] (domyślnie: 1.0)')
    p.add_argument('--warmup', type=int, default=100)
    p.add_argument('--output', default=None,
                   help='Plik CSV wyjściowy (domyślnie: auto)')
    p.add_argument('--turbo-off-reminder', action='store_true',
                   help='Wypisz przypomnienie o Turbo OFF przed pomiarem')
    return p.parse_args()


def main():
    args = parse_args()
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')

    if args.turbo_off_reminder:
        print('⚠  PRZYPOMNIENIE: Wyłącz Turbo Boost przed pomiarem!')
        print('   Intel: echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo')
        print('   AMD:   echo 0 > /sys/devices/system/cpu/cpufreq/boost\n')

    hostname = platform.node()
    print(f'Benchmark przepustowości XOF — {hostname}')
    print(f'Wejście: {INPUT_MSG_SIZE} B (stałe), min_time={args.min_time}s')
    print(f'Algorytmy: {", ".join(a.upper() for a in args.xofs)}')
    print(f'Rozmiary: {[size_label(s) for s in args.sizes]}\n')

    all_results = []
    header      = ['alg', 'output_bytes', 'output_label',
                   'throughput_mbs', 'time_per_call_s', 'n_iters', 'hostname']

    for alg in args.xofs:
        print(f'{alg.upper()}:')
        print(f'  {"Rozmiar":>8}  {"MB/s":>10}  {"Czas/wywołanie":>16}  {"Iteracje":>10}')
        print('  ' + '-' * 52)

        for size in args.sizes:
            result = measure_throughput(alg, size, args.min_time, args.warmup)
            label  = size_label(size)

            t_str = (f'{result["time_per_call_s"]*1e6:.1f} µs'
                     if result['time_per_call_s'] < 0.001 else
                     f'{result["time_per_call_s"]*1e3:.2f} ms'
                     if result['time_per_call_s'] < 1.0 else
                     f'{result["time_per_call_s"]:.3f} s')

            print(f'  {label:>8}  {result["throughput_mbs"]:>10.2f}  '
                  f'{t_str:>16}  {result["n_iters"]:>10,}')

            all_results.append({
                'alg':             alg,
                'output_bytes':    size,
                'output_label':    label,
                'throughput_mbs':  result['throughput_mbs'],
                'time_per_call_s': result['time_per_call_s'],
                'n_iters':         result['n_iters'],
                'hostname':        hostname,
            })
        print()

    # Zapis CSV
    out_dir = REPO_ROOT / 'data' / 'raw' / 'ch07_throughput'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = Path(args.output) if args.output else \
        out_dir / f'sweep_{hostname}_{ts}.csv'

    with open(out_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(all_results)

    print(f'Wyniki zapisane: {out_file}')


if __name__ == '__main__':
    main()
