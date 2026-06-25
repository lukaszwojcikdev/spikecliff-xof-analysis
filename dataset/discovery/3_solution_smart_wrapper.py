import hashlib
import time

class SmartSHAKE128:
    """
    Wrapper świadomy granic algorytmicznych (Algorithm-Aware).
    Zapobiega zjawisku SpikeCliff poprzez buforowanie.
    """
    def __init__(self):
        self.rate = 168  # Rate dla SHAKE128
        self.buffer = bytearray()
        self.state = hashlib.shake_128()

    def update(self, data):
        """
        Inteligentny update: przetwarza tylko pełne bloki,
        resztę zostawia w buforze na później.
        """
        self.buffer.extend(data)
        
        # Sprawdzamy, ile mamy pełnych bloków
        full_blocks_len = (len(self.buffer) // self.rate) * self.rate
        
        if full_blocks_len > 0:
            # Przetwarzamy TYLKO wielokrotności 168 bajtów (najtańszy koszt)
            chunk_to_process = self.buffer[:full_blocks_len]
            self.state.update(chunk_to_process)
            
            # Resztę (np. ten 1 nadmiarowy bajt) zostawiamy w buforze
            # Nie płacimy za nową permutację teraz!
            self.buffer = self.buffer[full_blocks_len:]

    def finalize(self, output_len):
        """Dopiero na samym końcu przetwarzamy resztki."""
        if self.buffer:
            self.state.update(self.buffer)
        return self.state.digest(output_len)

# --- TEST PORÓWNAWCZY (Rozwiązanie vs Naiwne podejście) ---

print("--- ETAP 3: Test Mitygacji (Rozwiązanie) ---")
ITERATIONS = 200000

# Scenariusz: Dostajemy dane w paczkach po 169 bajtów (najgorszy przypadek)
# Wyobraź sobie czujnik IoT wysyłający 169 bajtów co chwilę.
chunk_bad = b'A' * 169 

# 1. Podejście Naiwne (Bezpośrednie)
start = time.perf_counter()
state_naive = hashlib.shake_128()
for _ in range(ITERATIONS):
    # Każde wywołanie tutaj płaci karę za 2 permutacje!
    state_naive.update(chunk_bad)
naive_digest = state_naive.digest(32)
end = time.perf_counter()
time_naive = end - start

# 2. Podejście Smart (Twoje rozwiązanie)
start = time.perf_counter()
smart_hasher = SmartSHAKE128()
for _ in range(ITERATIONS):
    # Tutaj wrapper przetworzy 168 bajtów, a 1 bajt schowa do bufora.
    # W następnej iteracji dołoży ten 1 bajt do nowych 168... itd.
    # Efektywnie "wygładzamy" schodki.
    smart_hasher.update(chunk_bad)
smart_digest = smart_hasher.finalize(32)
end = time.perf_counter()
time_smart = end - start

print(f"Czas wykonania NAIVE (Standard): {time_naive:.4f} s")
print(f"Czas wykonania SMART (Solution): {time_smart:.4f} s")
speedup = ((time_naive - time_smart) / time_naive) * 100
print(f"--- ZYSK WYDAJNOŚCI: {speedup:.2f}% ---")

assert naive_digest == smart_digest, "Błąd: Wyniki skrótów muszą być identyczne!"
print("(Weryfikacja kryptograficzna: OK)")