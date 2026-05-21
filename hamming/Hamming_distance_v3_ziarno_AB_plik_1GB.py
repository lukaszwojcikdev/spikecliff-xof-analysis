import numpy as np
from tqdm import tqdm
import os

def calculate_hamming(file1, file2):
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)

    if size1 != size2:
        print(f"Błąd: Pliki mają różne rozmiary! ({size1} vs {size2})")
        return

    print(f"Analiza plików: {size1 / 1024**2:.2f} MB")
    
    # Blok 100 MB - optymalny dla szybkości i RAMu
    CHUNK_SIZE = 100 * 1024 * 1024 
    total_hamming = 0
    total_bits = size1 * 8

    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        pbar = tqdm(total=size1, unit='B', unit_scale=True, desc="Hamming Distance")
        
        while True:
            chunk1 = f1.read(CHUNK_SIZE)
            chunk2 = f2.read(CHUNK_SIZE)
            if not chunk1:
                break
            
            # Konwersja na tablice NumPy (uint8)
            arr1 = np.frombuffer(chunk1, dtype=np.uint8)
            arr2 = np.frombuffer(chunk2, dtype=np.uint8)
            
            # XOR wykrywa różnice bitowe
            diff = np.bitwise_xor(arr1, arr2)
            
            # Szybkie liczenie jedynek w bajtach (metoda wektorowa)
            total_hamming += np.unpackbits(diff).sum()
            
            pbar.update(len(chunk1))
        
        pbar.close()

    percentage = (total_hamming / total_bits) * 100
    print(f"\n--- WYNIKI ---")
    print(f"Całkowita liczba bitów:  {total_bits}")
    print(f"Odległość Hamminga:      {total_hamming}")
    print(f"Różnica procentowa:      {percentage:.6f} %")
    print(f"Interpretacja:           {'IDENTYCZNE' if total_hamming == 0 else 'RÓŻNE'}")

if __name__ == "__main__":
    # Tutaj wpisz nazwy swoich plików
    calculate_hamming("blake3_xof_1gb_ziarno_A.bin", "blake3_xof_1gb_ziarno_B.bin")
