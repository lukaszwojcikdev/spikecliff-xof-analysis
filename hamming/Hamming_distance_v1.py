import numpy as np
from tqdm import tqdm

try:
    with open("blake3_xof_1gb_v1.bin", "rb") as f:
        a = f.read()
    with open("blake3_xof_1gb_v2.bin", "rb") as f:
        b = f.read()

    if len(a) != len(b):
        print("Blad: Pliki maja rozne rozmiary!")
    else:
        print(f"Porównuje pliki o rozmiarze: {len(a)} bajtów")

        # Obliczanie odległości Hamminga z paskiem postępu
        hamming_distance = 0
        for x, y in tqdm(zip(a, b), total=len(a), desc="Obliczanie odleglosci Hamminga"):
            hamming_distance += bin(x ^ y).count("1")

        print(f"Odleglosc Hamminga: {hamming_distance}")

except FileNotFoundError as e:
    print(f"Blad: {e}")
except Exception as e:
    print(f"Blad: {e}")

