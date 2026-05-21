from blake3 import blake3

FILE_NAME = "blake3_xof_32gb_ziarno_A.bin"
GB_SIZE = 32
CHUNK_MB = 16
CHUNK_BYTES = CHUNK_MB * 1024 * 1024
TOTAL_ITERATIONS = (GB_SIZE * 1024) // CHUNK_MB

print(f"Generowanie {FILE_NAME} (32 GB)...")
hasher = blake3(b"ziarno_A")

with open(FILE_NAME, "wb") as f:
    for i in range(TOTAL_ITERATIONS):
        offset = i * CHUNK_BYTES
        f.write(hasher.digest(length=CHUNK_BYTES, seek=offset))
        if (i + 1) % 64 == 0: # Co ok. 1 GB
            print(f"Postęp: {(i+1)*CHUNK_MB/1024:.1f}/{GB_SIZE} GB")

print("Gotowe!")
