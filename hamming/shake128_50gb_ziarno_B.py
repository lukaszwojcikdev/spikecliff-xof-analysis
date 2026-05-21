from hashlib import shake_128

FILE_NAME = "shake128_xof_50gb_ziarno_B.bin"
GB_SIZE = 50
CHUNK_MB = 16
CHUNK_BYTES = CHUNK_MB * 1024 * 1024
TOTAL_ITERATIONS = (GB_SIZE * 1024) // CHUNK_MB

print(f"Generowanie {FILE_NAME} ({GB_SIZE} GB)...")
print(f"Chunk: {CHUNK_MB} MB, iteracji: {TOTAL_ITERATIONS}")

with open(FILE_NAME, "wb") as f:
    for i in range(TOTAL_ITERATIONS):
        seed = b"ziarno_B" + i.to_bytes(8, "little")
        chunk = shake_128(seed).digest(CHUNK_BYTES)
        f.write(chunk)

        if (i + 1) % 40 == 0:
            print(f"  Postep: {(i+1)*CHUNK_MB/1024:.1f}/{GB_SIZE} GB")

print(f"Gotowe! Plik: {FILE_NAME}")
