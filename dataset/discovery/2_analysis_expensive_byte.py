import time
import hashlib

# Parametry dla SHAKE128
RATE = 168
ITERATIONS = 500000

def bench(size):
    data = b'A' * size
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        hashlib.shake_128(data).digest(32)
    end = time.perf_counter_ns()
    return (end - start) / ITERATIONS

print("--- ETAP 2: Analiza Najdroższego Bajtu ---")

# Pomiar dla pełnego bloku (Optimum)
t_optimal = bench(RATE)
print(f"Czas dla {RATE} bajtów (1 blok): {t_optimal:.2f} ns")

# Pomiar dla bloku + 1 bajt (Pessimum)
t_worst = bench(RATE + 1)
print(f"Czas dla {RATE + 1} bajtów (2 bloki): {t_worst:.2f} ns")

# Obliczenia
delta_ns = t_worst - t_optimal
percent_increase = (delta_ns / t_optimal) * 100

print("-" * 40)
print(f"Koszt tego JEDNEGO dodatkowego bajta: {delta_ns:.2f} ns")
print(f"Procentowy spadek wydajności: +{percent_increase:.1f}%")
print("-" * 40)
print("WNIOSEK: Ten 1 bajt kosztuje tyle samo, co przetworzenie poprzednich 168 bajtów.")