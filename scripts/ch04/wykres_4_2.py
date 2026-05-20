# Dane z Tabeli 4.2

import matplotlib.pyplot as plt
import numpy as np

# Dane z tabeli
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']
passed = [109, 104, 103]
weak = [3, 10, 11]
failed = [2, 0, 0]
percent_passed_labels = ['95,6%', '91,2%', '90,4%']

# Pozycje na osi X
x = np.arange(len(algorithms))
width = 0.6  # Szerokość słupków

fig, ax = plt.subplots(figsize=(10, 6))

# Rysowanie słupków skumulowanych
# Kolor zielony dla PASSED
p1 = ax.bar(x, passed, width, label='PASSED', color='#a1d99b') 
# Kolor żółty/pomarańczowy dla WEAK (sumujemy od góry passed)
p2 = ax.bar(x, weak, width, bottom=passed, label='WEAK', color='#fd8d3c')
# Kolor czerwony dla FAILED (sumujemy od góry passed + weak)
p3 = ax.bar(x, failed, width, bottom=np.array(passed) + np.array(weak), label='FAILED', color='#fc4e2a')

# Dodawanie tytułu i etykiet
ax.set_ylabel('Liczba testów', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(algorithms, fontsize=12)
ax.set_ylim(0, 125)  # Nieco powyżej 114 (Razem), aby było miejsce na opisy

# Legenda
ax.legend(loc='upper left')

# Dodawanie siatki tylko na osi Y
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

# Dodawanie wartości % PASSED na górze słupków
for i, v in enumerate(percent_passed_labels):
    # Wysokość całkowita słupka to 114 (Razem)
    total_height = 114 
    ax.text(i, total_height + 2, f"% PASSED: {v}", ha='center', fontsize=11, fontweight='bold', color='black')

# Dodawanie liczb wewnątrz sekcji słupków (opcjonalne, dla czytelności)
def add_labels(rects, offset=0):
    for rect in rects:
        height = rect.get_height()
        if height > 0: # Nie wyświetlaj jeśli 0
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, rect.get_y() + height / 2 + offset),
                        ha='center', va='center', color='black', fontsize=10)

add_labels(p1)
add_labels(p2)
add_labels(p3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
