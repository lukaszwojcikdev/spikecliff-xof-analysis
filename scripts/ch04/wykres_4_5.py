import matplotlib.pyplot as plt
import numpy as np

# Dane z Tabeli 4.6 (kolumna "Odch. std.")
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']
sac_std_values = [0.02998, 0.03202, 0.03012]

# Kolory zbliżone do tych na obrazku
colors = ['#4B0082', '#C71585', '#E9967A'] # Ciemny fiolet, Różowy/Magenta, Jasny pomarańczowy

fig, ax = plt.subplots(figsize=(8, 5))

# Rysowanie słupków
bars = ax.bar(algorithms, sac_std_values, color=colors, width=0.6)

# Ustawienia tytułu (główny i podtytuł)
ax.set_title('SAC Test Analysis (Ideal = 0.5)', fontsize=14, fontweight='bold')
ax.set_xlabel('algorytm', fontsize=12)
ax.set_ylabel('sac_std', fontsize=12)

# Dodanie podtytułu "Odchylenie standardowe..."
ax.text(0.5, 1.05, 'Odchylenie standardowe (Mniejsze = Lepsze)', 
        horizontalalignment='center', 
        verticalalignment='bottom', 
        transform=ax.transAxes, 
        fontsize=11, 
        style='italic')

# Ustawienie zakresu osi Y
ax.set_ylim(0, 0.035)
ax.set_yticks(np.arange(0, 0.031, 0.005))

# Dodanie siatki poziomej
ax.grid(axis='y', linestyle='-', alpha=0.6)
ax.set_axisbelow(True)

# Dostosowanie układu
plt.tight_layout()

# Wyświetlenie wykresu
plt.show()
