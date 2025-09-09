import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import logging
import sys

# --- SETUP LOGGING ---
output_dir = r"D:\testing magang\Analisis_isu_PythonFile-main\Output"
os.makedirs(output_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(output_dir, "proses.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Lokasi input
input_file = r"D:\testing magang\Analisis_isu_PythonFile-main\Data\data_klasifikasi.json"

def analyze_data():
    logging.info("🚀 Memulai analisis klasifikasi...")
    logging.info(f"📂 Membaca data dari: {input_file}")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)["klasifikasi_tema"]
    except Exception as e:
        logging.error(f"❌ Gagal membaca file: {e}")
        return

    # Simpan semua kegiatan
    all_activities = []
    analysis_results = {}

    logging.info("--- Analisis Kuantitatif per Tema ---")

    for theme, activities in data.items():
        total_activities = len(activities)
        unique_activities = len(set(d["namakegiatan"] for d in activities))
        analysis_results[theme] = {
            "total_activities": total_activities,
            "unique_activities": unique_activities
        }
        all_activities.extend([d["namakegiatan"] for d in activities])

        logging.info(f"Tema: {theme}")
        logging.info(f"Jumlah total kegiatan: {total_activities}")
        logging.info(f"Jumlah kegiatan unik: {unique_activities}")

    # Identifikasi kegiatan yang paling sering muncul secara keseluruhan
    logging.info("--- Top 5 Kegiatan yang Paling Sering Muncul ---")
    overall_most_common = Counter(all_activities).most_common(5)
    for activity, count in overall_most_common:
        logging.info(f"'{activity}': {count} kali")

    # Analisis kegiatan yang sama (muncul lebih dari 1 kali)
    logging.info("--- Analisis Kegiatan yang Sama ---")
    duplicate_activities = {k: v for k, v in Counter(all_activities).items() if v > 1}
    total_duplicate_types = len(duplicate_activities)
    total_duplicate_count = sum(duplicate_activities.values())

    if duplicate_activities:
        for activity, count in duplicate_activities.items():
            logging.info(f"'{activity}' muncul {count} kali")
        logging.info(f"📊 Total jenis kegiatan duplikat: {total_duplicate_types}")
        logging.info(f"📊 Total kemunculan kegiatan duplikat: {total_duplicate_count}")
    else:
        logging.info("Tidak ada kegiatan yang sama ditemukan.")

    # =========================
    # Simpan hasil UNIK ke JSON
    # =========================
    unique_file_json = os.path.join(output_dir, "hasil_analisis_unique.json")
    output_unique = {
        "per_tema": analysis_results,
        "top5_kegiatan": overall_most_common
    }
    try:
        with open(unique_file_json, "w", encoding="utf-8") as f:
            json.dump(output_unique, f, indent=4, ensure_ascii=False)
        logging.info(f"✅ Hasil analisis unik disimpan ke: {unique_file_json}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan file unik: {e}")

    # Simpan hasil DUPLIKAT ke JSON
    duplicate_file_json = os.path.join(output_dir, "hasil_analisis_duplicate.json")
    output_duplicate = {
        "kegiatan_duplikat": duplicate_activities,
        "total_jenis_duplikat": total_duplicate_types,
        "total_kemunculan_duplikat": total_duplicate_count
    }
    try:
        with open(duplicate_file_json, "w", encoding="utf-8") as f:
            json.dump(output_duplicate, f, indent=4, ensure_ascii=False)
        logging.info(f"✅ Hasil analisis duplikat disimpan ke: {duplicate_file_json}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan file duplikat: {e}")

    # =========================
    # Simpan hasil ke Excel
    # =========================
    try:
        # Analisis Unik
        df_tema = pd.DataFrame.from_dict(analysis_results, orient="index").reset_index()
        df_tema.rename(columns={"index": "Tema"}, inplace=True)
        df_top5 = pd.DataFrame(overall_most_common, columns=["Kegiatan", "Jumlah Muncul"])

        excel_unique = os.path.join(output_dir, "hasil_analisis_unique.xlsx")
        with pd.ExcelWriter(excel_unique, engine="xlsxwriter") as writer:
            df_tema.to_excel(writer, sheet_name="Analisis Tema", index=False)
            df_top5.to_excel(writer, sheet_name="Top 5 Kegiatan", index=False)
        logging.info(f"✅ Hasil analisis unik Excel disimpan ke: {excel_unique}")

        # Analisis Duplikat
        df_duplikat = pd.DataFrame(list(duplicate_activities.items()), columns=["Kegiatan", "Jumlah Muncul"])
        df_duplikat.loc[len(df_duplikat.index)] = ["TOTAL JENIS DUPLIKAT", total_duplicate_types]
        df_duplikat.loc[len(df_duplikat.index)] = ["TOTAL KEMUNCULAN DUPLIKAT", total_duplicate_count]

        excel_duplicate = os.path.join(output_dir, "hasil_analisis_duplicate.xlsx")
        with pd.ExcelWriter(excel_duplicate, engine="xlsxwriter") as writer:
            df_duplikat.to_excel(writer, sheet_name="Kegiatan Duplikat", index=False)
        logging.info(f"✅ Hasil analisis duplikat Excel disimpan ke: {excel_duplicate}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan hasil Excel: {e}")

    # =========================
    # Visualisasi
    # =========================
    try:
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df_tema['Tema'], df_tema['unique_activities'],
                       color=['skyblue', 'salmon', 'lightgreen', 'orange', 'violet'])
        plt.xlabel('Tema')
        plt.ylabel('Jumlah Kegiatan Unik')
        plt.title('Jumlah Kegiatan Unik per Tema')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{int(yval)}',
                     ha='center', va='bottom')

        plt.tight_layout()
        img_file = os.path.join(output_dir, "unique_activities_per_theme.png")
        plt.savefig(img_file)
        plt.close()
        logging.info(f"✅ Visualisasi disimpan ke: {img_file}")
    except Exception as e:
        logging.error(f"❌ Gagal membuat visualisasi: {e}")

    logging.info("🎉 Analisis selesai. Semua hasil ada di folder Output.")


if __name__ == "__main__":
    analyze_data()
