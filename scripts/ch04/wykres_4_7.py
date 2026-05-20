import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# 1. Dane z tabeli 4.8
# ---------------------------------------------------------
rozmiary = [1, 10, 32, 50]
# Wartości surowe z tabeli
odchylenia_raw = [-0.000325, 0.000114, 0.000043, 0.000139]
# Na wykresie przedstawiono moduł odchylenia (wszystkie punkty > 0)
odchylenia_abs = [abs(d) for d in odchylenia_raw]

# ---------------------------------------------------------
# 2. Konfiguracja wykresu
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))

# Tło w kolorze jasnoniebieskim/szarym (jak na obrazku)
ax.set_facecolor('#EBF4F8')

# Rysowanie linii i markerów
ax.plot(rozmiary, odchylenia_abs, 
        marker='o', 
        color='#5B9BD5',          # Niebieski kolor linii
        linewidth=2, 
        markersize=7, 
        markeredgecolor='#3B74B3')

# Pozioma linia przerywana na Y=0
ax.axhline(0, color='#888888', linestyle='--', linewidth=1, alpha=0.8)

# Siatka (białe linie)
ax.grid(True, color='white', linestyle='-', linewidth=1.8)
ax.set_axisbelow(True) # Siatka rysowana pod elementami

# ---------------------------------------------------------
# 3. Oskalie i etykiety
# ---------------------------------------------------------
ax.set_ylim(-0.00002, 0.00034)
ax.set_yticks(np.arange(0, 0.00031, 0.00005))
ax.set_xticks(rozmiary)

# Formatowanie etykiet osi Y na 7 miejsc po przecinku (0.0000000, 0.0000500...)
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.7f}'))

ax.set_xlabel('Rozmiar [GB]', fontsize=11)
ax.set_ylabel('Odchył [%]', fontsize=11)

# Usunięcie ramek (spines) dla minimalistycznego wyglądu
for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_visible(False)

# Dostosowanie marginesów
plt.tight_layout()

# Wyświetlenie
plt.show()
