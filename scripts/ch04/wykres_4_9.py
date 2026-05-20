import matplotlib.pyplot as plt
import numpy as np

# Dane z tabeli
labels = ['32 B', '1 KB', '64 KB', '1 MB', '10 MB']
x = np.arange(len(labels))

# Przepustowość w MB/s
blake3_values = [17.94, 363.53, 937.40, 776.97, 793.37]
shake128_values = [3.08, 75.35, 332.06, 297.89, 306.49]
shake256_values = [2.89, 69.53, 273.91, 246.32, 256.23]

width = 0.25

fig, ax = plt.subplots(figsize=(11, 7))

# Rysowanie słupków
rects1 = ax.bar(x - width, blake3_values, width, label='BLAKE3', color='#3182bd')
rects2 = ax.bar(x, shake128_values, width, label='SHAKE128', color='#e377c2')
rects3 = ax.bar(x + width, shake256_values, width, label='SHAKE256', color='#ff7f0e')

# Ustawienia osi i tytułu
ax.set_ylabel('Przepustowość [MB/s]', fontsize=12)
ax.set_xlabel('Rozmiar wyjścia XOF', fontsize=12)

# Skala logarytmiczna
ax.set_yscale('log')
ax.set_yticks([10, 100, 1000])
# KLUCZOWA ZMIANA: Zmniejszenie dolnego limitu osi Y, aby małe słupki (32 B) były widoczne
ax.set_ylim(2, 1100) 

# Etykiety na osi X
ax.set_xticks(x)
ax.set_xticklabels(labels)

# Legenda
ax.legend(loc='upper left')

# Siatka
ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.3) # Bardziej subtelna siatka jak na wykresie
ax.set_axisbelow(True)

# Poprawiona adnotacja (pozioma strzałka jak na obrazku)
# Współrzędne dla strzałki porównującej BLAKE3 i SHAKE256 dla 64 KB
x_group_64kb = x[2]
y_blake3_64kb = blake3_values[2]
y_shake256_64kb = shake256_values[2]

# Strzałka od prawej (SHAKE256) do lewej (BLAKE3)
ax.annotate('BLAKE3\n~2.8-3.4x\nszybszy',
            xy=(x_group_64kb - width, y_blake3_64kb), 
            xytext=(x_group_64kb + width, y_blake3_64kb),
            arrowprops=dict(arrowstyle='<-', color='blue', lw=1.5), # Strzałka w lewo
            fontsize=10, color='blue', ha='center', va='bottom')


plt.tight_layout()
plt.show()
