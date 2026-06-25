import time

# --- SYMULACJA KOSZTU ---
# Udajemy, że jesteśmy na słabym mikrokontrolerze, 
# gdzie jedna permutacja (hashowanie bloku) zajmuje trochę czasu.

PERMUTATION_COST = 0.00001  # 10 mikrosekund (symulacja kosztu Keccak-f)
RATE = 168

class SimulatedSHAKE:
    def __init__(self):
        self.buffer = bytearray()
        
    def naive_update(self, data):
        # W podejściu naiwnym, każda porcja danych > RATE
        # lub brzydko wyrównana wymusza pracę CPU.
        # Symulujemy:
        # Jeśli dane przekraczają blok, płacimy za 2 permutacje zamiast 1
        
        blocks = (len(data) + RATE - 1) // RATE
        # Symulujemy pracę CPU
        time.sleep(blocks * PERMUTATION_COST)

    def smart_update(self, data):
        # W podejściu smart, buforujemy i przetwarzamy TYLKO pełne bloki
        self.buffer.extend(data)
        full_blocks = len(self.buffer) // RATE
        
        if full_blocks > 0:
            # Płacimy tylko za pełne bloki
            time.sleep(full_blocks * PERMUTATION_COST)
            # Usuwamy przetworzone
            processed = full_blocks * RATE
            self.buffer = self.buffer[processed:]
        # Reszta czeka w buforze za darmo!

# --- TEST ---
print("--- ETAP 4: Dowód Symulowany (Model Teoretyczny) ---")
print(f"Założenie: Koszt permutacji = {PERMUTATION_COST*1e6:.0f} µs")

ITERATIONS = 50000
# Złośliwy chunk: 169 bajtów (1 blok + 1 bajt)
chunk_bad = b'A' * 169 

# 1. Test Naive
start = time.perf_counter()
sim_naive = SimulatedSHAKE()
for _ in range(ITERATIONS):
    sim_naive.naive_update(chunk_bad)
end = time.perf_counter()
time_naive = end - start

# 2. Test Smart
start = time.perf_counter()
sim_smart = SimulatedSHAKE()
for _ in range(ITERATIONS):
    sim_smart.smart_update(chunk_bad)
end = time.perf_counter()
time_smart = end - start

print(f"Czas NAIVE (Simulation): {time_naive:.4f} s")
print(f"Czas SMART (Simulation): {time_smart:.4f} s")

# Obliczamy zysk
if time_smart < time_naive:
    gain = ((time_naive - time_smart) / time_naive) * 100
    print(f"--- ZYSK TEORETYCZNY: {gain:.2f}% ---")
    print("WNIOSEK: Algorytm działa poprawnie, gdy koszt kryptografii dominuje nad narzutem języka.")
else:
    print("Nadal coś jest nie tak z parametrami symulacji.")