import numpy as np
from tqdm import tqdm
import os
import sys
from datetime import datetime

def calculate_hamming(file1, file2, label=""):
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)

    if size1 != size2:
        print(f"Blad: Pliki maja rozne rozmiary! ({size1} vs {size2})")
        return None

    size_mb = size1 / 1024**2
    print(f"\nAnaliza: {label}")
    print(f"Pliki: {file1} vs {file2}")
    print(f"Rozmiar: {size_mb:.2f} MB")

    CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
    total_hamming = 0
    total_bits = size1 * 8

    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        pbar = tqdm(total=size1, unit='B', unit_scale=True, desc="Hamming Distance")
        while True:
            chunk1 = f1.read(CHUNK_SIZE)
            chunk2 = f2.read(CHUNK_SIZE)
            if not chunk1:
                break
            arr1 = np.frombuffer(chunk1, dtype=np.uint8)
            arr2 = np.frombuffer(chunk2, dtype=np.uint8)
            diff = np.bitwise_xor(arr1, arr2)
            total_hamming += np.unpackbits(diff).sum()
            pbar.update(len(chunk1))
        pbar.close()

    percentage = (total_hamming / total_bits) * 100
    deviation = abs(percentage - 50.0)

    print(f"\n--- WYNIKI ---")
    print(f"Calkowita liczba bitow:  {total_bits}")
    print(f"Odleglosc Hamminga:      {total_hamming}")
    print(f"Roznica procentowa:      {percentage:.6f} %")
    print(f"Odchylenie od 50%:       {deviation:.6f} %")
    print(f"Interpretacja:           {'IDENTYCZNE' if total_hamming == 0 else 'ROZNE'}")

    return {
        "label": label,
        "file1": file1,
        "file2": file2,
        "size_mb": size_mb,
        "total_bits": total_bits,
        "hamming": total_hamming,
        "percentage": percentage,
        "deviation": deviation
    }


def save_results(results, output_file):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Wyniki analizy odleglosci Hamminga — XOF\n")
        f.write(f"Data: {ts}\n")
        f.write("=" * 60 + "\n\n")
        for r in results:
            if r is None:
                continue
            f.write(f"Algorytm/Label:          {r['label']}\n")
            f.write(f"Plik A:                  {r['file1']}\n")
            f.write(f"Plik B:                  {r['file2']}\n")
            f.write(f"Rozmiar:                 {r['size_mb']:.2f} MB\n")
            f.write(f"Calkowita liczba bitow:  {r['total_bits']}\n")
            f.write(f"Odleglosc Hamminga:      {r['hamming']}\n")
            f.write(f"Roznica procentowa:      {r['percentage']:.6f} %\n")
            f.write(f"Odchylenie od 50%:       {r['deviation']:.6f} %\n")
            f.write("-" * 60 + "\n\n")
    print(f"\nWyniki zapisane do: {output_file}")


if __name__ == "__main__":
    # -------------------------------------------------------
    # Uruchom po wygenerowaniu wszystkich 4 par plikow:
    #   shake128_xof_50gb_ziarno_A.bin / _B.bin
    #   shake256_xof_50gb_ziarno_A.bin / _B.bin
    # -------------------------------------------------------

    pairs = [
        ("shake128_xof_50gb_ziarno_A.bin", "shake128_xof_50gb_ziarno_B.bin", "SHAKE128 XOF 50 GB (ziarno A vs B)"),
        ("shake256_xof_50gb_ziarno_A.bin", "shake256_xof_50gb_ziarno_B.bin", "SHAKE256 XOF 50 GB (ziarno A vs B)"),
    ]

    results = []
    for f1, f2, label in pairs:
        if not os.path.exists(f1) or not os.path.exists(f2):
            print(f"POMINIĘTO (brak pliku): {label}")
            continue
        r = calculate_hamming(f1, f2, label)
        results.append(r)

    if results:
        save_results(results, "wyniki_Hamming_SHAKE_50GB_ziarno_AB.txt")
    else:
        print("Brak plikow do analizy.")
