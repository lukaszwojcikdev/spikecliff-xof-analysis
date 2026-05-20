import matplotlib.pyplot as plt
import numpy as np

# Dane z tabeli 4.6
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']
sac_avg_values = [0.50094, 0.49873, 0.49913]
ideal_value = 0.50000


colors = ['#3b5998', '#2c8c8c', '#76c476']

fig, ax = plt.subplots(figsize=(8, 5))

# Rysowanie słupków
bars = ax.bar(algorithms, sac_avg_values, color=colors, width=0.6, edgecolor='black')

# Dodanie linii idealnej (0.5)
ax.axhline(y=ideal_value, color='red', linestyle='--', linewidth=2, label=f'Ideal {ideal_value}')

# Ustawienia tytułu i etykiet
ax.set_title('Średnia zmiana bitów (SAC)', fontsize=14, pad=15)
ax.set_ylabel('sac_avg', fontsize=12)
ax.set_xlabel('algorytm', fontsize=12)

# Ustawienie zakresu osi Y, aby pokazać drobne różnice (jak na obrazku)
ax.set_ylim(0.46, 0.54)
ax.set_yticks(np.arange(0.46, 0.55, 0.02))

# Dodanie siatki poziomej
ax.grid(axis='y', linestyle='-', linewidth=0.7, alpha=0.7)
ax.set_axisbelow(True) # Siatka pod słupkami

# Legenda
ax.legend(loc='upper right')

# Opcjonalnie: Dodanie wartości liczbowych nad słupkami dla precyzji
for bar, value in zip(bars, sac_avg_values):
    ax.annotate(f'{value:.5f}',
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10)


# Dostosowanie layoutu
plt.tight_layout()

# Wyświetlenie wykresu
plt.show()
