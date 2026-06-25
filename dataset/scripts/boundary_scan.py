#!/usr/bin/env python3
"""
scripts/ch06/boundary_scan.py
------------------------------
Główny skrypt boundary-aware profiling — implementacja metodologii
opisanej w §6.2 pracy (Listing 6.1).

Odpowiada skryptowi boundary_profiler.py cytowanemu w §6.2.

Użycie
------
  # SHAKE128 — zakres 110–400 B, krok 1 B, 1000 powtórzeń
  taskset -c 0 python scripts/ch06/boundary_scan.py \\
      --xof shake128 --start 110 --end 400 \\
      --step 1 --iterations 1000 \\
      --output data/raw/ch06_timing/scan_shake128.csv

  # SHAKE256
  taskset -c 0 python scripts/ch06/boundary_scan.py \\
      --xof shake256 --start 80 --end 340 \\
      --step 1 --iterations 1000 \\
      --output data/raw/ch06_timing/scan_shake256.csv

  # BLAKE3 (kontrola negatywna, §6.6)
  taskset -c 0 python scripts/ch06/boundary_scan.py \\
      --xof blake3 --start 110 --end 400 \\
      --step 1 --iterations 1000 \\
      --output data/raw/ch06_timing/scan_blake3.csv

Wymagania środowiskowe (dla wyników zgodnych z pracą)
-------------------------------------------------------
  - Turbo Boost / Precision Boost: OFF
  - CPU affinity: przypięcie do 1 rdzenia (taskset -c 0)
  - SMT/HT: zalecane OFF
  - Szczegóły: docs/HARDWARE_SETUP.md
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Dodaj src/ do ścieżki Pythona
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / 'src'))

from xof_generators import validate_determinism, XOFName
from timing_profiler import (
    profile_xof, save_results, detect_cliffs, validate_environment
)


def parse_args():
    p = argparse.ArgumentParser(
        description='Boundary-aware profiling funkcji XOF (SpikeCliff Effect)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument('--xof', required=True,
                   choices=['blake3', 'shake128', 'shake256'],
                   help='Algorytm XOF do profilowania')
    p.add_argument('--start', type=int, default=1,
                   help='Dolna granica skanowania [bajty] (domyślnie: 1)')
    p.add_argument('--end', type=int, default=600,
                   help='Górna granica skanowania [bajty] (domyślnie: 600)')
    p.add_argument('--step', type=int, default=1,
                   help='Krok skanowania [bajty] (domyślnie: 1 = rozdzielczość bajtowa)')
    p.add_argument('--iterations', type=int, default=1000,
                   help='Liczba powtórzeń per punkt (domyślnie: 1000)')
    p.add_argument('--output-len', type=int, default=32,
                   help='Rozmiar wyjścia XOF [bajty] (domyślnie: 32)')
    p.add_argument('--warmup', type=int, default=100,
                   help='Liczba iteracji warm-up (domyślnie: 100)')
    p.add_argument('--cpu-pin', type=int, default=None,
                   help='Numer rdzenia do przypięcia (domyślnie: bez przypięcia)')
    p.add_argument('--output', type=str, default=None,
                   help='Ścieżka wyjściowa CSV (domyślnie: auto)')
    p.add_argument('--skip-env-check', action='store_true',
                   help='Pomiń weryfikację konfiguracji środowiska')
    p.add_argument('--quiet', action='store_true',
                   help='Minimalne wyjście tekstowe')
    return p.parse_args()


def main():
    args = parse_args()
    verbose = not args.quiet

    print('=' * 60)
    print(f'  Boundary-Aware Profiling — {args.xof.upper()}')
    print(f'  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    # ── Weryfikacja środowiska ─────────────────────────────────────────
    if not args.skip_env_check:
        env = validate_environment()
        print('\nKonfiguracja środowiska:')
        for k, v in env.items():
            flag = '✓' if 'OFF' in str(v) or 'isolated' in k else '⚠'
            print(f'  {flag} {k}: {v}')

        if any('ON' in str(v) for v in env.values()):
            print('\n  ⚠ Zalecenie: wyłącz Turbo Boost i SMT przed pomiarem.')
            print('    Szczegóły: docs/HARDWARE_SETUP.md')
            print('    Kontynuować mimo to? [t/N] ', end='')
            if input().strip().lower() != 't':
                print('Anulowano.')
                sys.exit(0)

    # ── Walidacja deterministyczności ─────────────────────────────────
    print(f'\nWeryfikacja deterministyczności {args.xof.upper()}...')
    if not validate_determinism(args.xof):
        print('  BŁĄD: Generator nie jest deterministyczny!')
        sys.exit(1)
    print('  OK')

    # ── Ścieżka wyjściowa ─────────────────────────────────────────────
    if args.output is None:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'host'
        fname = f'scan_{args.xof}_{hostname}_{ts}.csv'
        output_path = REPO_ROOT / 'data' / 'raw' / 'ch06_timing' / fname
    else:
        output_path = Path(args.output)

    # ── Główny pomiar ──────────────────────────────────────────────────
    print(f'\nRozpoczynam profilowanie...')
    t_start = time.time()

    results = profile_xof(
        alg=args.xof,
        length_start=args.start,
        length_end=args.end,
        length_step=args.step,
        output_len=args.output_len,
        n_reps=args.iterations,
        warmup_reps=args.warmup,
        cpu_pin=args.cpu_pin,
        verbose=verbose,
    )

    elapsed = time.time() - t_start
    print(f'\nCzas pomiaru: {elapsed/60:.1f} min')

    # ── Zapis wyników ──────────────────────────────────────────────────
    save_results(results, output_path)

    # ── Automatyczna detekcja klifów ───────────────────────────────────
    print('\nDetekcja klifów (próg: 100 ns):')
    cliffs = detect_cliffs(results, min_jump_ns=100.0)

    if cliffs:
        for c in cliffs:
            print(f'  Klif @ {c["position_bytes"]} B: '
                  f'skok={c["jump_ns"]:.0f} ns  '
                  f'(przed={c["before_ns"]:.0f} → po={c["after_ns"]:.0f} ns)')
        print(f'\n  Znaleziono {len(cliffs)} klifów.')

        # Weryfikacja zgodności z granicami rate FIPS 202
        from timing_profiler import RATE_BYTES
        rate = RATE_BYTES.get(args.xof.lower())
        if rate:
            expected = [(k+1)*rate + 1 for k in range(
                args.start // rate, args.end // rate + 1
            ) if (k+1)*rate + 1 <= args.end]
            found_pos = [c['position_bytes'] for c in cliffs]
            matches   = [p for p in found_pos if p in expected]
            print(f'\n  Oczekiwane granice rate: {expected}')
            print(f'  Znalezione:              {found_pos}')
            print(f'  Zgodność z FIPS 202:     {len(matches)}/{len(expected)}')
    else:
        print('  Brak klifów > 100 ns — zgodne z oczekiwaniem dla BLAKE3.')

    print(f'\n  Dane zapisane: {output_path}')
    print('\nGotowe.')


if __name__ == '__main__':
    main()
