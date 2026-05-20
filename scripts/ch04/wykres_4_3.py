# Dane z Tabeli  4.4

import matplotlib.pyplot as plt
import numpy as np

# Dane z tabeli (wartości entropii H)
sample_sizes = ['100 MB', '1 GB', '10 GB']
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']

# Wartości H z tabeli dla poszczególnych algorytmów i rozmiarów próbek
data_H = {
    'BLAKE3': [0.999999998, 1.000000000, 1.000000000],
    'SHAKE128': [0.999999981, 0.999999981, 0.999999981],
    'SHAKE256': [0.999999945, 0.999999945, 0.999999945]
}

# Obliczanie odchyleń w ppm (parts per million, czyli * 10^6)
# Odchylenie = (1.0 - H) * 1,000,000
data_deviation = {}
for algo, values in data_H.items():
    data_deviation[algo] = [(1.0 - v) * 1e6 for v in values]

# Ustawienia wykresu
x = np.arange(len(sample_sizes))  # Lokalizacje etykiet na osi X
width = 0.25  # Szerokość słupków

fig, ax = plt.subplots(figsize=(10, 6))

# Rysowanie słupków dla każdego algorytmu
rects1 = ax.bar(x - width, data_deviation['BLAKE3'], width, label='BLAKE3', color='#3182bd')
rects2 = ax.bar(x, data_deviation['SHAKE128'], width, label='SHAKE128', color='#e377c2') # Różowy/czerwony
rects3 = ax.bar(x + width, data_deviation['SHAKE256'], width, label='SHAKE256', color='#ff7f0e')

# Dodawanie etykiet i tytułów
ax.set_ylabel('Odchylenie od H=1.0 [ppm = 10^-6]', fontsize=12)
ax.set_xlabel('Rozmiar próbki', fontsize=12)


# Ustawianie ticków na osi X
ax.set_xticks(x)
ax.set_xticklabels(sample_sizes)

# Dodawanie legendy
ax.legend()

# Funkcja dodająca wartości nad słupkami
def autolabel(rects):
    """Dołącz etykietę tekstową nad każdym słupkiem w rects, wyświetlając jego wysokość."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 punkty przesunięcia w pionie
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

# Dostosowanie osi Y (zakres) i siatki
ax.set_ylim(0, 0.06)
ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)
ax.set_axisbelow(True) # Siatka pod słupkami


# Dostosowanie layoutu
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # rect zostawia miejsce na źródło u dołu

# Wyświetlenie wykresu
plt.show()
