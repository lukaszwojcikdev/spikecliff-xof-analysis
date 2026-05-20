import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Dane wejściowe (same wartości liczbowe z tabeli)
data = [
    [1, 1, 2, 0, 2, 1, 0],   # monobit_test
    [1, 3, 2, 1, 0, 2, 1],   # frequency_within_block_test
    [2, 0, 1, 1, 2, 1, 2],   # runs_test
    [1, 1, 1, 1, 1, 1, 1],   # longest_run...
    [0, 0, 0, 0, 1, 1, 0],   # binary_matrix...
    [1, 0, 1, 4, 0, 1, 0],   # dft_test
    [0, 0, 1, 0, 0, 0, 0],   # non_overlapping...
    [1, 1, 1, 1, 1, 2, 0],   # overlapping...
    [1, 4, 0, 0, 0, 0, 2],   # maurers...
    [0, 1, 1, 2, 2, 2, 1],   # linear_complexity...
    [1, 1, 2, 2, 3, 2, 2],   # serial_test
    [1, 1, 2, 1, 1, 1, 1],   # approximate_entropy...
    [2, 1, 1, 2, 3, 1, 0],   # cumulative_sums...
    [11, 9, 3, 6, 9, 9, 12], # random_excursion...
    [11, 6, 9, 12, 13, 12, 9]# random_excursion_variant...
]

# Krótkie nazwy testów (zgodnie ze stylem z Rysunku 4.1)
short_test_names = [
    'monobit', 'blk_freq', 'runs', 'long_run', 'matrix', 
    'DFT', 'non-OL', 'overlap', 'univ.', 'lin.compl.', 
    'serial', 'approx_H', 'cumsum', 'rand_exc', 'rand_exc_v'
]

# Etykiety kolumn z Twoich danych
column_labels = [
    'BLK3 2Mb', 'BLK3 10Mb', 'BLK3 50Mb', 
    'S128 2Mb', 'S128 10Mb', 
    'S256 2Mb', 'S256 10Mb'
]

# Tworzenie DataFrame
df = pd.DataFrame(data, index=short_test_names, columns=column_labels)

# Konfiguracja wykresu
plt.figure(figsize=(14, 7))

# Generowanie heat mapy
# cmap='YlOrRd' zapewnia skalę od żółtego do czerwonego, podobną do oryginału
# linewidths=1 i linecolor='white' dodają białe ramki do komórek dla czytelności
heatmap = sns.heatmap(
    df, 
    annot=True,          # Wyświetla liczby w środku
    fmt="d",             # Format liczb całkowitych
    cmap="YlOrRd",       # Paleta kolorów
    linewidths=1,        # Grubość linii siatki
    linecolor='white',   # Kolor linii siatki
    cbar_kws={'label': 'Liczba FAILów'} # Etykieta paska kolorów
)

# Tytuł wykresu
plt.title('Heatmapa wyników NIST SP 800-22 — porównanie algorytmów i rozmiarów', fontsize=14, pad=20)

# Obrócenie etykiet osi X, aby się nie nakładały
plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(rotation=0, fontsize=11)

# Dodanie informacji o sumach na dole (opcjonalnie, jako tekst)
# Ponieważ heatmapa operuje na macierzy liczb, wiersze tekstowe ("SUMA", "%") 
# są lepiej oddane poniżej wykresu lub w osobnej tabeli. Tutaj dodaję je jako tekst.
plt.figtext(
    0.5, 0.01, 
    "SUMA FAILów: [34, 29, 27, 33, 38, 36, 31] | % plików z ≥1 FAIL: [24%, 24%, 19%, 19%, 32%, 25%, 28%]", 
    ha="center", fontsize=10, style='italic', wrap=True
)

plt.tight_layout()
plt.show()
