# SpikeCliff Effect — Measurement Data and Analysis Scripts

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

## Overview


The **SpikeCliff Effect** is a deterministic timing discontinuity occurring in
extendable-output functions (XOF) based on the sponge construction. It manifests
as regular processing-time spikes at input lengths that cross the rate boundary,
caused by additional Keccak-f[1600] permutation calls. The effect is fully
predictable from FIPS 202 parameters and reproducible across hardware platforms.

### Key results at a glance

| Algorithm | Rate (r) | Boundary Byte (B*) | Cliff amplitude | Model R² |
|-----------|----------|--------------------|-----------------|----------|
| SHAKE128  | 168 B    | 169, 337, 505 B    | ~240–260 cycles | 0.998    |
| SHAKE256  | 136 B    | 137, 273, 409 B    | ~240–260 cycles | 0.998    |
| BLAKE3    | —        | none               | none            | — (negative control) |

Boundary Byte position reproducibility: **±0.0 B** across 10 independent
measurement series with Turbo Boost disabled.

---

## Repository Structure

```
spikecliff-xof-analysis/
│
├── README.md                     — this file
├── requirements.txt              — Python dependencies
│
├── dataset/src/                  — core modules (required by boundary_scan.py)
│   ├── xof_generators.py         — unified XOF interface (BLAKE3, SHAKE128, SHAKE256)
|   ├── boundary_scan.py          — main CLI scanner (uses src/ modules)
|   ├── boundary_profiler.py      — boundary-aware profiling core module for per-byte timing analysis
|   ├── gamma_functions.py        — localized statistical wrapper with numerically stable fallback for large-scale test suites
│   └── timing_profiler.py        — boundary-aware profiling engine
│
├── dataset/scripts/                             — measurement and figure scripts
│   ├── boundary_scan.py                         — main CLI scanner (uses src/ modules)
│   ├── spikecliff_scanner_shake128.py           — standalone SHAKE128 scan → Figure 1
│   ├── spikecliff_scanner_shake256_v2.py        — standalone SHAKE256 scan → Figure 2
│   ├── compare_timings_i9_No_TurboB_shake128.py — Turbo ON vs OFF → Figure 3
│   ├── figure_4_blake3.py                       — BLAKE3 negative control → Figure 4
│   └── wykres_6_6.py                            — Figure 4 variant (Polish labels)
│
├── dataset/figures/                   — final figures as published
│   ├── spikecliff_shake128_plot.png   — Figure 1: SHAKE128 stepwise timing profile
│   └── spikecliff_shake256_plot.png   — Figure 2: SHAKE256 stepwise timing profile
│
├── dataset/raw_data/                     — original measurement data
│   ├── spikecliff_shake128_results.txt   — SHAKE128 per-size timing (14.01.2026)
│   ├── spikecliff_shake256_results.txt   — SHAKE256 per-size timing (14.01.2026)
│   ├── STEC_LIVE_i9_shake128_081531_TurboB_no_stress.7z
│   ├── STEC_LIVE_i9_shake128_082738_TurboB_stress.7z
│   ├── STEC_LIVE_i9_shake128_085741_No_TurboB_no_stress.7z
│   └── STEC_LIVE_i9_shake128_092643_No_TurboB_stress.7z
│
└── dataset/discovery/                 — chronological record of the discovery process
    ├── 1_discovery_spikecliff.py      — initial anomaly detection
    ├── 2_analysis_expensive_byte.py   — cost analysis of the boundary byte
    ├── 3_solution_smart_wrapper.py    — mitigation prototype (SmartSHAKE128)
    └── 4_simulation_proof.py          — theoretical cost model simulation
```

---

## Quickstart

### 1. Clone and install dependencies

```bash
git clone https://github.com/lukaszwojcikdev/spikecliff-xof-analysis.git
cd spikecliff-xof-analysis
pip install -r requirements.txt
```

### 2. Disable Turbo Boost (required for clean results)

**Linux — Intel:**
```bash
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
```

**Linux — AMD:**
```bash
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost
```

**Windows:** disable Intel Turbo Boost Technology and Intel Speed Step in BIOS,
or use [ThrottleStop](https://www.techpowerup.com/download/techpowerup-throttlestop/).

> **Note on HP t630:** The AMD GX-420MC (Jaguar microarchitecture) has no Turbo
> Boost at the hardware level — it is the ideal baseline platform and requires
> no DVFS configuration.

### 3. Run the scans

**Figure 1 — SHAKE128 stepwise profile (standalone, no src/ needed):**
```bash
taskset -c 0 python dataset/scripts/spikecliff_scanner_shake128.py
```
Expected: cliff detected at **169 B** (r+1, r=168 B per FIPS 202).

**Figure 2 — SHAKE256 stepwise profile (standalone):**
```bash
taskset -c 0 python dataset/scripts/spikecliff_scanner_shake256_v2.py
```
Expected: cliff detected at **137 B** (r+1, r=136 B per FIPS 202).

**Figure 4 — BLAKE3 negative control (standalone):**
```bash
python dataset/scripts/figure_4_blake3.py
```
Expected: no regular cliffs — confirms sponge specificity of SpikeCliff.

**Full boundary scan with CSV output (requires src/):**
```bash
taskset -c 0 python dataset/scripts/boundary_scan.py \
    --xof shake128 --start 1 --end 600 \
    --step 1 --iterations 1000 --cpu-pin 0
```

---

## Reproduction Notes

### Expected runtimes

| Script | Platform | Turbo | Runtime |
|--------|----------|-------|---------|
| `spikecliff_scanner_shake128.py` | i9 Raptor Lake | OFF | ~15–20 min |
| `spikecliff_scanner_shake256_v2.py` | i9 Raptor Lake | OFF | ~15–20 min |
| `figure_4_blake3.py` | any | any | ~5 min |

### Verification checklist

- [ ] Turbo Boost / Precision Boost disabled
- [ ] Process pinned to single core (`taskset -c 0`)
- [ ] Cliff at exactly 169 B for SHAKE128
- [ ] Cliff at exactly 137 B for SHAKE256
- [ ] No cliff for BLAKE3

### Raw data format

`spikecliff_shake128_results.txt` / `spikecliff_shake256_results.txt`:
```
Size (B) | Mean (ns) | Median (ns) | ns/byte | Visual bar
```

`STEC_LIVE_*.7z` archives — chunk-access timing data for Figure 3
(Turbo ON vs OFF comparison under CPU load), column: `duration_ns`.

---

## Hardware Platforms Used

| Platform    | CPU                           | Arch         | RAM        | OS                          | Role                         |
|-------------|-------------------------------|--------------|------------|-----------------------------|------------------------------|
| Intel i9    | Core i9 (P+E, AVX2, Raptor Lake) | x86-64    | 32 GB DDR5 | Win 11 + WSL2 Ubuntu 22.04  | Primary SpikeCliff measurement |
| AMD Ryzen 5 | Ryzen 5 3550H (AVX2, Zen+)   | x86-64 12 nm | 32 GB DDR4 | Win 11 + WSL2 Ubuntu 22.04  | Determinism verification     |
| HP t630     | AMD GX-420MC (Jaguar, no AVX2) | x86-64 28 nm | 16 GB DDR4 | Linux Mint 21.2 kernel 5.19 | Turbo OFF baseline           |

The consistency of SpikeCliff boundary positions across all three platforms —
including the HP t630 which lacks AVX2 entirely — confirms that the effect is
independent of SIMD instruction set availability.

---

## Mathematical Model

The execution time of a sponge-based XOF follows:

```
T(L) = α·L + β·⌊L/r⌋ + ε
```

where:
- `α` — cost of processing 1 byte in continuous mode [cycles/B]
- `β` — additional cost of a Boundary Byte [cycles/permutation]  
- `⌊L/r⌋` — number of full rate blocks for input length L
- `ε` — residual noise

Fitted parameters (Turbo OFF, x86-64):

| Parameter      | SHAKE128    | SHAKE256    |
|----------------|-------------|-------------|
| α [cycles/B]   | 11–12       | 11–12       |
| β [cycles]     | 240–260     | 250–270     |
| β/α ratio      | 12–13%      | 14–15%      |
| R²             | ≥ 0.998     | ≥ 0.998     |

---

## Citation


---

## License

Code and data: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

---

## Contact

**Łukasz Wójcik**   
ORCID: [https://orcid.org/0009-0005-3249-1312]  
Email: kontakt[at]lukaszwojcik.eu
