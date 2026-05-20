import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =================================================================
# 🛠️ - Porównanie średniego czasu bloku XOF (skala liniowa) dla trzech algorytmów
# =================================================================
# Jeśli któregoś pliku nie masz, zostaw cudzysłów pusty "" lub wpis None

FILE_BLAKE3 = "STEC_LOG_110003_blake3.csv"
FILE_K12    = "STEC_K12_120007_k12.csv"
FILE_SHAKE  = "STEC_SHAKE256_130010_shake.csv"

# =================================================================

def load_and_prep(filename, label):
    if not filename or not os.path.exists(filename):
        print(f"⚠️  Pominięto: {label} (Brak pliku: '{filename}')")
        return None

    print(f"📖 Wczytywanie: {filename} ({label})...")
    df = pd.read_csv(filename)

    # Parsowanie czasu
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    df['datetime'] = pd.to_datetime(today + ' ' + df['wall_clock'])
    start_time = df['datetime'].iloc[0]

    # Resampling co 1 sekundę (średnia)
    df.set_index('datetime', inplace=True)
    resampled = df['duration_ns'].resample('1s').mean()

    # Budowa DataFrame do wykresu
    final_df = pd.DataFrame()
    final_df['duration_ns'] = resampled
    final_df['minutes'] = (resampled.index - start_time).total_seconds() / 60.0
    final_df['Algorithm'] = label

    final_df.reset_index(drop=True, inplace=True)
    return final_df

def plot_manual_comparison():
    print("🚀 Rozpoczynam analizę porównawczą...")

    data_frames = []

    # Ładowanie poszczególnych plików
    df_b = load_and_prep(FILE_BLAKE3, "BLAKE3")
    if df_b is not None: data_frames.append(df_b)

    df_k = load_and_prep(FILE_K12, "KangarooTwelve")
    if df_k is not None: data_frames.append(df_k)

    df_s = load_and_prep(FILE_SHAKE, "SHAKE256")
    if df_s is not None: data_frames.append(df_s)

    if not data_frames:
        print("❌ Nie załadowano żadnych danych! Sprawdź nazwy plików w sekcji KONFIGURACJA.")
        return

    # Łączenie w jedną tabelę
    full_data = pd.concat(data_frames)

    print("🎨 Rysowanie wykresu...")
    plt.figure(figsize=(16, 10))
    sns.set_style("whitegrid")

    # Rysowanie linii
    # Kolory: BLAKE3 (Zielony), K12 (Pomarańcz), SHAKE (Czerwony/Fiolet)
    sns.lineplot(data=full_data, x='minutes', y='duration_ns', hue='Algorithm',
                 linewidth=2.5, palette='bright')

    # Dodatki graficzne (Stres i Real-World)
    # Zakładamy, że testy były robione w podobnym schemacie czasowym
    plt.axvspan(10, 20, color='gray', alpha=0.15, label='Obszar Ataku (Stress)')

    # Tytuły
    plt.title("Analiza Porównawcza STEC: Wrażliwość algorytmów na szum systemowy", fontsize=16, fontweight='bold')
    plt.xlabel("Czas trwania eksperymentu (minuty)", fontsize=12)
    plt.ylabel("Średni czas bloku (ns) - Skala Liniowa", fontsize=12)

    # Legenda
    plt.legend(title="Algorytm XOF", fontsize=12, loc='upper left')

    # Zapis
    output_file = "STEC_MANUAL_COMPARE.png"
    plt.savefig(output_file, dpi=300)
    print(f"✅ Wykres gotowy: {output_file}")
    plt.show()

if __name__ == "__main__":
    plot_manual_comparison()
