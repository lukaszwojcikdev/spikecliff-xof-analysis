"""
SpikeCliff Scanner
==================
Empirical detection of boundary cost discontinuities in XOF (SHAKE128/256).

The SpikeCliff Effect: A ~150x cost spike occurs when input crosses the 
rate boundary (r), forcing an additional Keccak-f[1600] permutation.

Author: Your Name
Date: 2026-01-14
"""

import time
import hashlib
import statistics
import os
import sys
from typing import List, Tuple

# =============================================================================
# CONFIGURATION
# =============================================================================

# Algorithm selection
ALGORITHM = "SHAKE128"  # Options: "SHAKE128" or "SHAKE256"
OUTPUT_SIZE = 32  # bytes (doesn't affect SpikeCliff, but kept consistent)

# Block sizes (rate parameter 'r' in bytes)
BLOCK_SIZES = {
    "SHAKE128": 168,  # 1344 bits
    "SHAKE256": 136   # 1088 bits
}

BLOCK_SIZE = BLOCK_SIZES[ALGORITHM]

# Scan range: test around the boundary
# We scan ±18 bytes around r, and up to 2*r+20 to see second cliff
START_SIZE = max(1, BLOCK_SIZE - 18)
END_SIZE = BLOCK_SIZE * 2 + 20

# Measurement parameters
ITERATIONS = 100_000  # Number of repetitions per size
WARMUP_ITERATIONS = 500  # Warm-up iterations to stabilize CPU/cache

# Spike detection threshold
SPIKE_THRESHOLD = 1.12  # 12% increase = potential spike

# Output options
SAVE_TO_FILE = True
OUTPUT_FILE = f"spikecliff_{ALGORITHM.lower()}_results.txt"
SHOW_PROGRESS = True

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_hash_function(algo: str):
    """Return the appropriate hash function."""
    if algo == "SHAKE128":
        return hashlib.shake_128
    elif algo == "SHAKE256":
        return hashlib.shake_256
    else:
        raise ValueError(f"Unknown algorithm: {algo}")

def benchmark_size(size: int, iterations: int, warmup: int) -> Tuple[float, float, float]:
    """
    Benchmark a specific input size.
    
    Returns:
        (mean_ns, median_ns, stddev_ns)
    """
    hash_func = get_hash_function(ALGORITHM)
    
    # Generate random data once
    data = os.urandom(size)
    
    # Warm-up phase: stabilize CPU frequency, fill caches
    for _ in range(warmup):
        h = hash_func(data)
        h.digest(OUTPUT_SIZE)
    
    # Measurement phase
    timings = []
    
    # We measure in batches to reduce timing overhead
    BATCH_SIZE = min(1000, iterations)
    num_batches = iterations // BATCH_SIZE
    
    for _ in range(num_batches):
        t0 = time.perf_counter_ns()
        for _ in range(BATCH_SIZE):
            h = hash_func(data)
            h.digest(OUTPUT_SIZE)
        t1 = time.perf_counter_ns()
        
        # Time per operation
        batch_time = (t1 - t0) / BATCH_SIZE
        timings.append(batch_time)
    
    # Statistics
    mean_ns = statistics.mean(timings)
    median_ns = statistics.median(timings)
    
    # Standard deviation (if enough samples)
    if len(timings) > 1:
        stddev_ns = statistics.stdev(timings)
    else:
        stddev_ns = 0.0
    
    return mean_ns, median_ns, stddev_ns

def detect_spike(results: List[Tuple[int, float]], threshold: float = SPIKE_THRESHOLD) -> str:
    """
    Detect if current result shows a spike compared to previous.
    
    Returns:
        Marker string if spike detected, empty string otherwise.
    """
    if len(results) < 2:
        return ""
    
    prev_time = results[-2][1]
    curr_time = results[-1][1]
    
    if curr_time > prev_time * threshold:
        increase_pct = ((curr_time / prev_time) - 1) * 100
        return f" 🏔️  SPIKECLIFF! (+{increase_pct:.1f}%)"
    
    return ""

def create_ascii_bar(value: float, min_val: float, max_val: float, width: int = 40) -> str:
    """Create an ASCII bar chart."""
    if max_val <= min_val:
        return "█"
    
    normalized = (value - min_val) / (max_val - min_val)
    bar_length = int(normalized * width)
    return "█" * max(1, bar_length)

# =============================================================================
# MAIN SCANNER
# =============================================================================

def run_spikecliff_scan():
    """Main scanning function."""
    
    print("=" * 80)
    print(f"SpikeCliff Scanner — {ALGORITHM}")
    print("=" * 80)
    print(f"Theoretical boundary (r): {BLOCK_SIZE} bytes")
    print(f"Expected SpikeCliff at:   {BLOCK_SIZE + 1} bytes (r+1)")
    print(f"Scan range:               {START_SIZE}—{END_SIZE} bytes")
    print(f"Iterations per size:      {ITERATIONS:,}")
    print(f"Warmup iterations:        {WARMUP_ITERATIONS:,}")
    print("=" * 80)
    print()
    
    # Storage for results
    results = []
    
    # Header
    header = f"{'Size (B)':<10} | {'Mean (ns)':<12} | {'Median (ns)':<12} | {'ns/byte':<10} | {'Visual'}"
    print(header)
    print("-" * 80)
    
    # Open output file if needed
    if SAVE_TO_FILE:
        outfile = open(OUTPUT_FILE, 'w', encoding='utf-8')
        outfile.write(f"SpikeCliff Scanner Results — {ALGORITHM}\n")
        outfile.write(f"Boundary: {BLOCK_SIZE} bytes\n")
        outfile.write("=" * 80 + "\n")
        outfile.write(header + "\n")
        outfile.write("-" * 80 + "\n")
    
    try:
        # Scan loop
        for size in range(START_SIZE, END_SIZE + 1):
            # Benchmark this size
            mean_ns, median_ns, stddev_ns = benchmark_size(
                size, 
                ITERATIONS, 
                WARMUP_ITERATIONS
            )
            
            # Store result
            results.append((size, mean_ns, median_ns, stddev_ns))
            
            # Cost per byte
            cost_per_byte = mean_ns / size
            
            # ASCII visualization (normalize to current data range)
            if len(results) > 1:
                all_times = [r[1] for r in results]
                min_time = min(all_times)
                max_time = max(all_times)
                bar = create_ascii_bar(mean_ns, min_time, max_time, width=30)
            else:
                bar = "█"
            
            # Spike detection
            spike_marker = detect_spike(results, SPIKE_THRESHOLD)
            
            # Special marker for theoretical boundary
            boundary_marker = ""
            if size == BLOCK_SIZE:
                boundary_marker = " ← r (boundary)"
            elif size == BLOCK_SIZE + 1:
                boundary_marker = " ← r+1 (EXPECTED SPIKE)"
            elif size == BLOCK_SIZE * 2:
                boundary_marker = " ← 2r (second boundary)"
            elif size == BLOCK_SIZE * 2 + 1:
                boundary_marker = " ← 2r+1 (second spike)"
            
            # Format output line
            line = (f"{size:<10} | "
                   f"{mean_ns:>10.2f} ns | "
                   f"{median_ns:>10.2f} ns | "
                   f"{cost_per_byte:>8.2f} ns | "
                   f"{bar}{spike_marker}{boundary_marker}")
            
            print(line)
            
            if SAVE_TO_FILE:
                outfile.write(line + "\n")
                outfile.flush()
            
            # Progress indicator
            if SHOW_PROGRESS and size % 10 == 0:
                progress = (size - START_SIZE) / (END_SIZE - START_SIZE) * 100
                sys.stdout.write(f"\rProgress: {progress:.1f}%")
                sys.stdout.flush()
        
        # Clear progress line
        if SHOW_PROGRESS:
            sys.stdout.write("\r" + " " * 40 + "\r")
            sys.stdout.flush()
    
    finally:
        if SAVE_TO_FILE:
            outfile.close()
    
    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    # Find the biggest spikes
    spikes = []
    for i in range(1, len(results)):
        prev_size, prev_time, _, _ = results[i-1]
        curr_size, curr_time, _, _ = results[i]
        
        if curr_time > prev_time * SPIKE_THRESHOLD:
            increase = (curr_time / prev_time - 1) * 100
            spikes.append((curr_size, increase))
    
    if spikes:
        print(f"\nDetected {len(spikes)} significant spikes:")
        for size, increase in sorted(spikes, key=lambda x: -x[1])[:5]:
            expected = ""
            if size == BLOCK_SIZE + 1:
                expected = " ✓ EXPECTED (r+1)"
            elif size == BLOCK_SIZE * 2 + 1:
                expected = " ✓ EXPECTED (2r+1)"
            print(f"  • Size {size} bytes: +{increase:.1f}%{expected}")
    else:
        print("\n⚠️  No significant spikes detected.")
        print("Possible reasons:")
        print("  - Python overhead dominates (try C implementation)")
        print("  - CPU frequency scaling interfering (disable turbo boost)")
        print("  - Insufficient iterations (increase ITERATIONS)")
    
    # Summary statistics
    print(f"\nSummary:")
    print(f"  Fastest: {min(r[1] for r in results):.2f} ns (size {min(results, key=lambda x: x[1])[0]} B)")
    print(f"  Slowest: {max(r[1] for r in results):.2f} ns (size {max(results, key=lambda x: x[1])[0]} B)")
    print(f"  Range:   {max(r[1] for r in results) / min(r[1] for r in results):.2f}×")
    
    if SAVE_TO_FILE:
        print(f"\n✓ Results saved to: {OUTPUT_FILE}")
    
    print("=" * 80)
    
    return results

# =============================================================================
# VISUALIZATION (Optional — requires matplotlib)
# =============================================================================

def plot_results(results: List[Tuple[int, float, float, float]]):
    """
    Create a visualization of the SpikeCliff effect.
    Requires: pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n⚠️  matplotlib not installed. Skipping plot.")
        print("Install with: pip install matplotlib")
        return
    
    sizes = [r[0] for r in results]
    means = [r[1] for r in results]
    medians = [r[2] for r in results]
    
    plt.figure(figsize=(12, 6))
    
    # Main plot
    plt.plot(sizes, means, 'b-', linewidth=1, label='Mean time', alpha=0.7)
    plt.plot(sizes, medians, 'g--', linewidth=1, label='Median time', alpha=0.5)
    
    # Mark boundaries
    plt.axvline(BLOCK_SIZE, color='red', linestyle='--', 
                linewidth=2, label=f'r = {BLOCK_SIZE} bytes', alpha=0.7)
    plt.axvline(BLOCK_SIZE * 2, color='orange', linestyle='--', 
                linewidth=2, label=f'2r = {BLOCK_SIZE * 2} bytes', alpha=0.7)
    
    plt.xlabel('Input Size (bytes)', fontsize=12)
    plt.ylabel('Time (nanoseconds)', fontsize=12)
    plt.title(f'SpikeCliff Effect in {ALGORITHM}', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    plot_filename = f"spikecliff_{ALGORITHM.lower()}_plot.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {plot_filename}")
    
    # Show plot (optional — comment out if running headless)
    # plt.show()

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("\n🏔️  Starting SpikeCliff Scanner...\n")
    
    # Run the scan
    results = run_spikecliff_scan()
    
    # Optional: Create visualization
    try:
        plot_results(results)
    except Exception as e:
        print(f"\n⚠️  Could not create plot: {e}")
    
    print("\n✓ SpikeCliff scan complete!\n")