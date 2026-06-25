"""
src/timing_profiler.py
----------------------
Boundary-aware profiling funkcji XOF — główny moduł Rozdziału 6.

Implementuje metodologię opisaną w §6.2 pracy:
- Skan długości wejścia z rozdzielczością 1 bajtu
- time.perf_counter_ns() o rozdzielczości nanosekundowej
- k=1000 powtórzeń per punkt, mediana jako miara odporna
- Pinowanie wątku do rdzenia (Linux: os.sched_setaffinity)
- Warm-up 100 iteracji przed pomiarami właściwymi

Detektowany efekt: SpikeCliff Effect — deterministyczne skoki mediany
przy przekroczeniu granic bloku rate konstrukcji sponge.

Granice rate (FIPS 202):
  SHAKE128: r = 168 B → klif przy 169, 337, 505 B …
  SHAKE256: r = 136 B → klif przy 137, 273, 409 B …
  BLAKE3:   brak regularnych klifów (architektura drzewiasta)
"""

from __future__ import annotations
import gc
import os
import sys
import time
import csv
import numpy as np
from pathlib import Path
from typing import Optional

# Importujemy interfejs generatorów z tego samego pakietu
sys.path.insert(0, str(Path(__file__).parent))
from xof_generators import hash_message, XOFName

# Granice rate wynikające z FIPS 202
RATE_BYTES = {
    'shake128': 168,
    'shake256': 136,
    'blake3':   None,   # brak regularnych granic sponge
}


def profile_xof(
    alg: XOFName,
    length_start: int = 1,
    length_end: int = 600,
    length_step: int = 1,
    output_len: int = 32,
    n_reps: int = 1000,
    warmup_reps: int = 100,
    cpu_pin: Optional[int] = None,
    verbose: bool = True,
) -> dict:
    """
    Profiluje czas wykonania XOF w funkcji długości wejścia.

    Parametry
    ---------
    alg          : algorytm XOF ('blake3' | 'shake128' | 'shake256')
    length_start : dolna granica skanowania [bajty]
    length_end   : górna granica skanowania [bajty]
    length_step  : krok skanowania [bajty] (1 = rozdzielczość bajtowa)
    output_len   : stały rozmiar wyjścia XOF [bajty] (domyślnie 32)
    n_reps       : liczba powtórzeń per punkt pomiarowy
    warmup_reps  : liczba iteracji warm-up (cache + predyktor gałęzi)
    cpu_pin      : numer rdzenia do przypięcia (None = bez przypięcia)
    verbose      : wypisuj postęp co 50 punktów

    Zwraca
    ------
    dict z kluczami:
        'lengths'   : np.ndarray int   — zakres długości wejścia [B]
        'medians'   : np.ndarray float — mediana czasu [ns]
        'means'     : np.ndarray float — średnia czasu [ns]
        'p05'       : np.ndarray float — percentyl 5 [ns]
        'p95'       : np.ndarray float — percentyl 95 [ns]
        'stds'      : np.ndarray float — odchylenie standardowe [ns]
        'alg'       : str              — nazwa algorytmu
        'n_reps'    : int              — liczba powtórzeń
        'rate_bytes': int | None       — granica rate z FIPS 202

    Uwagi metodologiczne
    --------------------
    - Garbage collector wyłączony podczas pomiarów (gc.disable/enable)
    - Warm-up ustabilizuje cache L1/L2, predyktor gałęzi i stan termiczny
    - Mediana odporna na outliers OS (przerwania, scheduler)
    - Dla reprodukcji wyników z pracy użyj: cpu_pin=0, Turbo Boost OFF
    """
    # Pinowanie do rdzenia (Linux)
    if cpu_pin is not None:
        try:
            os.sched_setaffinity(0, {cpu_pin})
            if verbose:
                print(f'  CPU pinned to core {cpu_pin}')
        except (AttributeError, OSError) as e:
            if verbose:
                print(f'  Ostrzeżenie: pinowanie CPU niedostępne ({e})')

    lengths = np.arange(length_start, length_end + 1, length_step)
    n_points = len(lengths)

    medians = np.empty(n_points)
    means   = np.empty(n_points)
    p05s    = np.empty(n_points)
    p95s    = np.empty(n_points)
    stds    = np.empty(n_points)

    if verbose:
        print(f'  Algorytm: {alg.upper()}')
        print(f'  Zakres: {length_start}–{length_end} B, krok={length_step} B')
        print(f'  Punkty: {n_points}, powtórzenia: {n_reps}, warm-up: {warmup_reps}')

    # Warm-up — ustabilizowanie cache i predyktora gałęzi
    warmup_msg = bytes(length_start)
    for _ in range(warmup_reps):
        hash_message(alg, warmup_msg, output_len)

    gc.disable()
    try:
        for i, l in enumerate(lengths):
            msg = bytes(l)  # deterministyczne wejście zerowe
            times = np.empty(n_reps)

            for k in range(n_reps):
                t0 = time.perf_counter_ns()
                hash_message(alg, msg, output_len)
                times[k] = time.perf_counter_ns() - t0

            medians[i] = np.median(times)
            means[i]   = np.mean(times)
            p05s[i]    = np.percentile(times, 5)
            p95s[i]    = np.percentile(times, 95)
            stds[i]    = np.std(times)

            if verbose and (i + 1) % 50 == 0:
                print(f'  [{i+1:4d}/{n_points}] l={l:4d} B  '
                      f'mediana={medians[i]:.0f} ns  '
                      f'p95={p95s[i]:.0f} ns')
    finally:
        gc.enable()

    return {
        'lengths':    lengths,
        'medians':    medians,
        'means':      means,
        'p05':        p05s,
        'p95':        p95s,
        'stds':       stds,
        'alg':        alg,
        'n_reps':     n_reps,
        'rate_bytes': RATE_BYTES.get(alg.lower()),
    }


def save_results(results: dict, output_path: str | Path) -> None:
    """
    Zapisuje wyniki profilowania do pliku CSV.

    Format: length_bytes, median_ns, mean_ns, p05_ns, p95_ns, std_ns

    Parametry
    ---------
    results     : słownik zwrócony przez profile_xof()
    output_path : ścieżka do pliku CSV wyjściowego
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'length_bytes', 'median_ns', 'mean_ns',
            'p05_ns', 'p95_ns', 'std_ns',
        ])
        for i in range(len(results['lengths'])):
            writer.writerow([
                int(results['lengths'][i]),
                float(results['medians'][i]),
                float(results['means'][i]),
                float(results['p05'][i]),
                float(results['p95'][i]),
                float(results['stds'][i]),
            ])

    print(f'  Zapisano: {output_path} ({len(results["lengths"])} punktów)')


def load_results(csv_path: str | Path) -> dict:
    """
    Wczytuje wyniki profilowania z pliku CSV.

    Zwraca słownik zgodny ze strukturą zwracaną przez profile_xof().
    """
    data = np.loadtxt(csv_path, delimiter=',', skiprows=1)
    return {
        'lengths': data[:, 0].astype(int),
        'medians': data[:, 1],
        'means':   data[:, 2],
        'p05':     data[:, 3],
        'p95':     data[:, 4],
        'stds':    data[:, 5],
    }


def detect_cliffs(
    results: dict,
    min_jump_ns: float = 100.0,
    window: int = 3,
) -> list[dict]:
    """
    Automatyczna detekcja klifów w profilu czasowym.

    Klif = skok mediany przekraczający min_jump_ns między
    średnią z window punktów przed i window punktów po.

    Parametry
    ---------
    results     : wyniki z profile_xof() lub load_results()
    min_jump_ns : minimalna amplituda skoku do klasyfikacji jako klif [ns]
    window      : szerokość okna uśredniającego

    Zwraca
    ------
    Lista słowników: [{'position_bytes': int, 'jump_ns': float}, ...]
    """
    lengths = results['lengths']
    medians = results['medians']
    cliffs  = []

    for i in range(window, len(medians) - window):
        before = np.mean(medians[i-window:i])
        after  = np.mean(medians[i:i+window])
        jump   = after - before
        if jump > min_jump_ns:
            cliffs.append({
                'position_bytes': int(lengths[i]),
                'jump_ns':        float(jump),
                'before_ns':      float(before),
                'after_ns':       float(after),
            })

    return cliffs


def validate_environment() -> dict:
    """
    Weryfikuje konfigurację środowiska pomiarowego.
    Używane przez scripts/ch06/boundary_scan.py przed pomiarem.

    Zwraca słownik ze statusem każdego parametru.
    """
    status = {}

    # Turbo Boost (Intel)
    turbo_path = Path('/sys/devices/system/cpu/intel_pstate/no_turbo')
    if turbo_path.exists():
        val = turbo_path.read_text().strip()
        status['turbo_intel'] = 'OFF' if val == '1' else 'ON (zalecane OFF)'
    else:
        # AMD Precision Boost
        boost_path = Path('/sys/devices/system/cpu/cpufreq/boost')
        if boost_path.exists():
            val = boost_path.read_text().strip()
            status['turbo_amd'] = 'OFF' if val == '0' else 'ON (zalecane OFF)'
        else:
            status['turbo'] = 'nieznany (sprawdź BIOS)'

    # SMT / Hyper-Threading
    smt_path = Path('/sys/devices/system/cpu/smt/active')
    if smt_path.exists():
        val = smt_path.read_text().strip()
        status['smt'] = 'ON (zalecane OFF dla pomiarów)' if val == '1' else 'OFF'

    # Izolowane rdzenie
    iso_path = Path('/sys/devices/system/cpu/isolated')
    if iso_path.exists():
        val = iso_path.read_text().strip()
        status['isolated_cpus'] = val if val else 'brak (zalecane isolcpus)'

    # CPU affinity bieżącego procesu
    try:
        affinity = os.sched_getaffinity(0)
        status['process_affinity'] = sorted(affinity)
    except AttributeError:
        status['process_affinity'] = 'niedostępne (Windows/macOS)'

    return status
