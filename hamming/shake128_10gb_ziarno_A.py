from hashlib import shake_128

FILE_NAME = "shake128_xof_10gb_ziarno_A.bin"
GB_SIZE = 10
CHUNK_MB = 16
CHUNK_BYTES = CHUNK_MB * 1024 * 1024
TOTAL_ITERATIONS = (GB_SIZE * 1024) // CHUNK_MB

print(f"Generowanie {FILE_NAME} ({GB_SIZE} GB)...")
print(f"Chunk: {CHUNK_MB} MB, iteracji: {TOTAL_ITERATIONS}")

# SHAKE128 nie ma natywnego seek jak BLAKE3 XOF,
# więc generujemy ciągły strumień przez kolejne niezależne wywołania
# z unikalnym licznikiem wbudowanym w seed — zachowuje deterministyczność
with open(FILE_NAME, "wb") as f:
    for i in range(TOTAL_ITERATIONS):
        # Seed: ziarno_A + numer bloku (little-endian 8 bajtów)
        seed = b"ziarno_A" + i.to_bytes(8, "little")
        chunk = shake_128(seed).digest(CHUNK_BYTES)
        f.write(chunk)

        if (i + 1) % 40 == 0:  # co ok. 640 MB
            print(f"  Postep: {(i+1)*CHUNK_MB/1024:.1f}/{GB_SIZE} GB")

print(f"Gotowe! Plik: {FILE_NAME}")
