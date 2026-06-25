"""
src/xof_generators.py
---------------------
Ujednolicony interfejs do generatorów XOF: BLAKE3, SHAKE128, SHAKE256.

Używany przez wszystkie skrypty i notebooki — zapewnia spójność ziarna,
deterministyczność i jednolite API niezależnie od biblioteki backendowej.

Zależności: blake3, pycryptodome
"""

from __future__ import annotations
import hashlib
import numpy as np
from typing import Literal

XOFName = Literal['blake3', 'shake128', 'shake256']
SUPPORTED = ('blake3', 'shake128', 'shake256')


def generate_stream(
    alg: XOFName,
    n_bytes: int,
    seed: bytes = b'xof_multidim_seed_2026',
) -> bytes:
    """
    Generuje deterministyczny strumień bajtów XOF.

    Parametry
    ---------
    alg     : nazwa algorytmu ('blake3' | 'shake128' | 'shake256')
    n_bytes : żądana długość wyjścia [bajty]
    seed    : ziarno wejściowe (domyślne zachowuje reprodukowalność)

    Zwraca
    ------
    bytes o długości n_bytes

    Przykłady
    ---------
    >>> stream = generate_stream('shake128', 1024)
    >>> len(stream)
    1024
    """
    alg = alg.lower()
    if alg not in SUPPORTED:
        raise ValueError(f'Nieobsługiwany algorytm: {alg}. Wybierz z: {SUPPORTED}')

    if alg == 'blake3':
        try:
            import blake3
            return blake3.blake3(seed).digest(length=n_bytes)
        except ImportError:
            raise ImportError('Zainstaluj blake3: pip install blake3')

    elif alg == 'shake128':
        try:
            from Crypto.Hash import SHAKE128
            h = SHAKE128.new()
            h.update(seed)
            return h.read(n_bytes)
        except ImportError:
            # Fallback do hashlib (Python 3.6+)
            h = hashlib.shake_128(seed)
            return h.digest(n_bytes)

    else:  # shake256
        try:
            from Crypto.Hash import SHAKE256
            h = SHAKE256.new()
            h.update(seed)
            return h.read(n_bytes)
        except ImportError:
            h = hashlib.shake_256(seed)
            return h.digest(n_bytes)


def generate_array(
    alg: XOFName,
    n_bytes: int,
    seed: bytes = b'xof_multidim_seed_2026',
    dtype=np.uint8,
) -> np.ndarray:
    """
    Generuje strumień XOF jako tablicę NumPy.

    Parametry
    ---------
    alg     : nazwa algorytmu
    n_bytes : żądana długość [bajty]
    seed    : ziarno wejściowe
    dtype   : typ elementów tablicy (domyślnie uint8)

    Zwraca
    ------
    np.ndarray dtype=uint8 (lub wskazany), kształt (n_bytes,)
    """
    raw = generate_stream(alg, n_bytes, seed)
    return np.frombuffer(raw, dtype=dtype)


def hash_message(
    alg: XOFName,
    message: bytes,
    output_len: int = 32,
) -> bytes:
    """
    Oblicza XOF z podanej wiadomości (nie z ziarna).
    Używane przy pomiarach czasowych i testach SAC.

    Parametry
    ---------
    alg        : nazwa algorytmu
    message    : wiadomość wejściowa
    output_len : długość wyjścia [bajty] (domyślnie 32 B)

    Zwraca
    ------
    bytes o długości output_len
    """
    alg = alg.lower()
    if alg not in SUPPORTED:
        raise ValueError(f'Nieobsługiwany algorytm: {alg}')

    if alg == 'blake3':
        import blake3
        return blake3.blake3(message).digest(length=output_len)

    elif alg == 'shake128':
        try:
            from Crypto.Hash import SHAKE128
            h = SHAKE128.new()
            h.update(message)
            return h.read(output_len)
        except ImportError:
            return hashlib.shake_128(message).digest(output_len)

    else:  # shake256
        try:
            from Crypto.Hash import SHAKE256
            h = SHAKE256.new()
            h.update(message)
            return h.read(output_len)
        except ImportError:
            return hashlib.shake_256(message).digest(output_len)


def validate_determinism(
    alg: XOFName,
    n_bytes: int = 1024,
    seed: bytes = b'determinism_check',
    n_runs: int = 5,
) -> bool:
    """
    Weryfikuje deterministyczność: n_runs wywołań musi dać identyczny wynik.
    Używane przez cross_platform_validator.py (R6).

    Zwraca True jeśli wyniki są identyczne, False w przeciwnym razie.
    """
    results = [generate_stream(alg, n_bytes, seed) for _ in range(n_runs)]
    return all(r == results[0] for r in results[1:])


# ── CLI helper ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    print('Weryfikacja generatorów XOF...')
    for alg in SUPPORTED:
        ok = validate_determinism(alg)
        stream = generate_stream(alg, 32)
        print(f'  {alg:10s}: deterministyczny={ok}, '
              f'pierwsze 8 B = {stream[:8].hex()}')
    print('OK')
