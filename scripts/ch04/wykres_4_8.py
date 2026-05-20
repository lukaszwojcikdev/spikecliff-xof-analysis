import matplotlib.pyplot as plt

# Dane na podstawie wykresu
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']

# Oś lewa (niebieska) - CPU_avg_%
cpu_values = [3, 9, 5]

# Oś prawa (zielona) - Czas (s)
time_values = [0.020, 0.010, 0.020]

# Utworzenie figury i głównej osi
fig, ax1 = plt.subplots(figsize=(8, 5))

# --- Rysowanie osi lewej (CPU) ---
color_cpu = 'tab:blue'
ax1.set_xlabel('algorytm', fontsize=12, fontweight='bold')
ax1.set_ylabel('CPU_avg_%', color=color_cpu, fontsize=11)
ax1.plot(algorithms, cpu_values, color=color_cpu, marker='o', markersize=8, linewidth=2, label='CPU %')
ax1.tick_params(axis='y', labelcolor=color_cpu)
ax1.set_ylim(3, 9)
ax1.set_yticks(range(3, 10))

# --- Tworzenie osi prawej (Czas) ---
ax2 = ax1.twinx()  
color_time = 'tab:green'
ax2.set_ylabel('Czas (s)', color=color_time, fontsize=11)
ax2.plot(algorithms, time_values, color=color_time, marker='s', markersize=7, linewidth=2, label='Czas (s)')
ax2.tick_params(axis='y', labelcolor=color_time)
ax2.set_ylim(0.010, 0.020)
# Ustawienie ticków co 0.002
ax2.set_yticks([0.010, 0.012, 0.014, 0.016, 0.018, 0.020])

# --- Tytuł i Siatka ---
plt.title('Wydajność: CPU vs Czas', fontsize=14, pad=15)
ax1.grid(True, linestyle='--', alpha=0.5)

# --- Legendy ---
# Umieszczenie legend wewnątrz obszaru wykresu
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Dostosowanie układu
fig.tight_layout()

# Wyświetlenie
plt.show()
