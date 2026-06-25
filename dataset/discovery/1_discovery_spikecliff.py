import time
import hashlib
import matplotlib.pyplot as plt
import statistics

# KONFIGURACJA
ALGO_NAME = "shake_128"
# Rate dla SHAKE128 to 168 bajtów. To jest nasza teoretyczna granica.
BLOCK_RATE = 168 
START_SIZE = 150
END_SIZE = 350
ITERATIONS = 100000  # Wysoka liczba dla stabilności statystycznej

def measure_execution(size):
    data = b'\x00' * size
    h_func = hashlib.shake_128
    
    # Warm-up (rozgrzewka cache CPU)
    for _ in range(1000):
        h_func(data).digest(32)

    # Sekcja krytyczna pomiaru
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        h_func(data).digest(32)
    end = time.perf_counter_ns()
    
    return (end - start) / ITERATIONS

print(f"--- ETAP 1: Skanowanie anomalii dla {ALGO_NAME} ---")
print(f"Szukamy skoku wydajności w okolicach {BLOCK_RATE} bajtów...\n")

sizes = []
times = []

for s in range(START_SIZE, END_SIZE):
    t = measure_execution(s)
    sizes.append(s)
    times.append(t)
    
    # Wykrywanie "Najdroższego Bajtu" w locie
    if len(times) > 1:
        prev_t = times[-2]
        if t > prev_t * 1.4: # Jeśli czas skoczył o >40%
            print(f"[!] WYKRYTO SPIKECLIFF: {s-1} -> {s} bajtów.")
            print(f"    Wzrost czasu: {prev_t:.2f} ns -> {t:.2f} ns")

# Rysowanie wykresu (opcjonalne, zapis do pliku)
plt.figure(figsize=(10, 6))
plt.plot(sizes, times, label='Czas wykonania (ns)')
plt.axvline(x=BLOCK_RATE, color='r', linestyle='--', label=f'Granica r={BLOCK_RATE}')
plt.axvline(x=BLOCK_RATE*2, color='orange', linestyle='--', label=f'Granica 2r={BLOCK_RATE*2}')
plt.title(f'Zjawisko SpikeCliff w {ALGO_NAME}')
plt.xlabel('Rozmiar wejścia (bajty)')
plt.ylabel('Czas (ns)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('spikecliff_discovery.png')
print("\n[OK] Wykres zapisano jako spikecliff_discovery.png")
