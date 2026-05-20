import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# 1. Dane z Tabeli      4.10
# ---------------------------------------------------------
algorithms = ['BLAKE3', 'SHAKE128', 'SHAKE256']

# Wartości surowe
nist_10m_fail_pct = [24, 32, 28]          # % plików z ≥1 FAIL (mniej = lepiej)
nist_5m_pass_rate = [1.0, 1.0, 1.0]       # 5/5 PASS (więcej = lepiej)
dieharder_pass_pct  = [109/114, 104/114, 103/114] # % PASSED
entropy_score       = [1.0, 1.0, 1.0]     # ~100% entropii
chi2_p_values       = [0.59, 0.10, 0.57]  # p-value (bliżej 0.5 = lepiej)
sac_deviation       = [0.00094, -0.00127, -0.00087] # odchylenie od 0.5
hamming_p_values    = [0.50000139, 0.50000059, 0.49999950] # bliżej 0.5 = lepiej
throughput_max      = [937, 332, 274]     # MB/s (więcej = lepiej)

# ---------------------------------------------------------
# 2. Normalizacja do skali 0.0 - 1.0 (1.0 = optimum)
# ---------------------------------------------------------
# Dla każdej metryki stosujemy inną logikę normalizacji:
v_nist_10m = [1 - (x / 100) for x in nist_10m_fail_pct]
v_nist_5m  = nist_5m_pass_rate
v_dieharder= dieharder_pass_pct
v_entropy  = entropy_score
v_chi2     = [0.9 + 0.1 * (1 - 2 * abs(p - 0.5)) for p in chi2_p_values] # Skala 0.9-1.0 dla PASS
v_sac      = [1 - 2 * abs(d) for d in sac_deviation]
v_hamming  = [1 - 2 * abs(p - 0.5) for p in hamming_p_values]
v_through  = [t / max(throughput_max) for t in throughput_max]

# Złożenie wektorów w macierz [algorytmy x kryteria]
stats = np.array([
    v_nist_10m, v_nist_5m, v_dieharder, v_entropy,
    v_chi2, v_sac, v_hamming, v_through
]).T  # Transpozycja, aby wiersze = algorytmy, kolumny = kryteria

# Krótkie etykiety osi
labels = [
    'NIST (10 Mbit)', 'NIST (5 MB)', 'Dieharder (1 GB)',
    'Entropia', 'Chi-kwadrat', 'SAC', 'Hamming', 'Przepustowość'
]
num_vars = len(labels)

# Kąty dla wykresu biegunowego
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # Zamknięcie pętli

# Dodanie pierwszego wiersza na koniec, aby wykres się zamykał
stats_plot = np.concatenate((stats, stats[:, [0]]), axis=1)

# ---------------------------------------------------------
# 3. Rysowanie wykresu
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

colors = ['#3182bd', '#e377c2', '#ff7f0e']

for i, algo in enumerate(algorithms):
    ax.plot(angles, stats_plot[i], color=colors[i], linewidth=2, label=algo)
    ax.fill(angles, stats_plot[i], color=colors[i], alpha=0.20)

# Ustawienie etykiet osi X (kryteria)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=10, rotation=30, ha='right')

# Ustawienie osi Y (wartości znormalizowane)
ax.set_ylim(0, 1)
ax.set_yticks(np.arange(0.2, 1.1, 0.2))
ax.set_yticklabels([f"{v:.1f}".replace('.', ',') for v in np.arange(0.2, 1.1, 0.2)], fontsize=9)
ax.grid(True, linestyle='--', alpha=0.6)

# Tytuł
ax.set_title(
    "Zestawienie zbiorcze XOF - profil wielokryterialny\n"
    "(wartości znormalizowane; 1,0 = wynik optymalny)",
    va='bottom', fontsize=12, pad=25, fontweight='bold'
)

# Legenda poza obszarem wykresu
ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.15), fontsize=10)


# Dostosowanie layoutu
plt.tight_layout()
plt.show()
