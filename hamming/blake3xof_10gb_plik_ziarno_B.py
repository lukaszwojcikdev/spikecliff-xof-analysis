from blake3 import blake3

FILE_NAME = "blake3_xof_10gb_ziarno_B.bin"
GB_SIZE = 10
CHUNK_MB = 16
CHUNK_BYTES = CHUNK_MB * 1024 * 1024
TOTAL_ITERATIONS = (GB_SIZE * 1024) // CHUNK_MB

print(f"Generowanie {FILE_NAME}...")
hasher = blake3(b"ziarno_B")

with open(FILE_NAME, "wb") as f:
    for i in range(TOTAL_ITERATIONS):
        offset = i * CHUNK_BYTES
        f.write(hasher.digest(length=CHUNK_BYTES, seek=offset))
        if (i + 1) % 40 == 0: # Co ok. 640 MB
            print(f"Postęp: {(i+1)*CHUNK_MB/1024:.1f}/{GB_SIZE} GB")

print("Gotowe!")
