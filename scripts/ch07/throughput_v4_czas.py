import time
import os
from Cryptodome.Hash import SHAKE128, SHAKE256
import blake3

def generate_shake128(data, out_len):
    h = SHAKE128.new(data)
    return h.read(out_len)

def generate_shake256(data, out_len):
    h = SHAKE256.new(data)
    return h.read(out_len)

def generate_blake3(data, out_len):
    return blake3.blake3(data).digest(length=out_len)

def benchmark_both(algo_func, data, output_bytes, min_duration=1.0):
    # Rozgrzewka (Warm-up)
    for _ in range(100):
        algo_func(data, output_bytes)
        
    # Auto-scale (szukanie odpowiedniej liczby iteracji)
    iters = 1
    while True:
        t0 = time.perf_counter()
        for _ in range(iters): 
            algo_func(data, output_bytes)
        elapsed = time.perf_counter() - t0
        if elapsed > 0.1: 
            break
        iters *= 10
        
    time_per_iter = elapsed / iters
    target_iters = int(min_duration / time_per_iter) + 1
    
    # Właściwy pomiar
    t0 = time.perf_counter()
    for _ in range(target_iters): 
        algo_func(data, output_bytes)
    total_time = time.perf_counter() - t0
    
    # Obliczenia Wyników
    time_sec = total_time / target_iters # Czas JEDNEGO wykonania w sekundach
    mb_per_sec = (output_bytes / 1_000_000) / time_sec # Przepustowość w MB/s
    
    return mb_per_sec, time_sec

if __name__ == "__main__":
    # Stałe wejście: 1 KB danych
    input_data = os.urandom(1024)
    
    # Rozmiary dopasowane do Twojej tabeli z Excela
    sizes = [32, 1024, 65536, 1048576, 2097152, 10485760, 52428800, 104857600] 
    size_labels = ["32B", "1KB", "64KB", "1MB", "2MB", "10MB", "50MB", "100MB"]
    
    algos = {
        "BLAKE3": generate_blake3,
        "SHAKE128": generate_shake128,
        "SHAKE256": generate_shake256
    }

    # Słowniki na wyniki
    results_mbps = {name: [] for name in algos}
    results_time = {name: [] for name in algos}

    # Ostrzeżenie, bo większe pliki będą testowane dłuższą chwilę
    # Przekierowujemy to do stderr, żeby nie śmieciło w pliku CSV
    import sys
    print("Trwa testowanie... To zajmie kilka minut ze względu na rozmiary 50MB i 100MB.", file=sys.stderr)

    for name, func in algos.items():
        for size in sizes:
            # Dla dużych rozmiarów (powyżej 10MB) algorytm i tak mieli długo,
            # więc skracamy minimalny czas trwania pętli pomiarowej, by skrypt nie działał godzinami.
            test_duration = 2.0 if size >= 10485760 else 1.0 
            
            mbps, time_sec = benchmark_both(func, input_data, size, test_duration)
            
            # Formatujemy liczby po polsku (przecinek)
            results_mbps[name].append(f"{mbps:.2f}".replace('.', ','))
            results_time[name].append(f"{time_sec:.6f}".replace('.', ','))
            
    # --- GENEROWANIE TABELI 1: PRZEPUSTOWOŚĆ ---
    header = ";".join(size_labels)
    print("Algorytm;" + header)
    for name in algos:
        print(f"{name};" + ";".join(results_mbps[name]))
        
    print("") # Pusta linia odstępu
    
    # --- GENEROWANIE TABELI 2: CZAS W SEKUNDACH ---
    time_header = ";".join(["sekundy"] * len(sizes))
    print("Czas;" + time_header)
    for name in algos:
        print(f"{name};" + ";".join(results_time[name]))
