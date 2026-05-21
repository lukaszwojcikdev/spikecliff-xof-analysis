from blake3 import blake3
import os

# Parametry
FILE_NAME = "blake3_xof_1gb_ziarno_B.bin"
TOTAL_SIZE_MB = 1024  # 1 GB
CHUNK_SIZE_MB = 1     # 1 MB na raz (oszczędność RAMu)

print(f"Generowanie pliku {FILE_NAME}...")

hasher = blake3(b"ziarno_B") # Twój seed

with open(FILE_NAME, "wb") as f:
    for i in range(TOTAL_SIZE_MB):
        # W BLAKE3 tryb XOF uzyskuje się przez digest() z podaniem długości
        # Używamy offsetu (i * CHUNK), aby symulować ciągły strumień XOF
        chunk = hasher.digest(length=CHUNK_SIZE_MB * 1024 * 1024, seek=i * CHUNK_SIZE_MB * 1024 * 1024)
        f.write(chunk)

        if (i + 1) % 100 == 0:
            print(f"Postęp: {i + 1}/{TOTAL_SIZE_MB} MB")

print("Gotowe! Plik wygenerowany.")
