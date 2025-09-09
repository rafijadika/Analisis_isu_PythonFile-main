import json
import os
import sys
import logging

# --- SETUP LOGGING ---
OUTPUT_FOLDER = "Output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_FOLDER, "proses.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Path ke file json
INPUT_FILE = os.path.join("Data", "data_klasifikasi.json")

def analisis_tema():
    # Load file JSON
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"✅ File {INPUT_FILE} berhasil dimuat.")
    except FileNotFoundError:
        logging.error(f"❌ File {INPUT_FILE} tidak ditemukan.")
        return
    except json.JSONDecodeError:
        logging.error(f"❌ File {INPUT_FILE} bukan JSON valid.")
        return

    # Ambil semua tema
    semua_tema = list(data.get("klasifikasi_tema", {}).keys())
    
    if not semua_tema:
        logging.warning("⚠️ Tidak ada tema di file JSON.")
        return

    # Tampilkan daftar tema
    logging.info("📌 Daftar Tema Tersedia:")
    for idx, tema in enumerate(semua_tema, start=1):
        logging.info(f"{idx}. {tema}")

    # Pilih tema
    try:
        pilihan = int(input("\nPilih nomor tema: "))
        tema_terpilih = semua_tema[pilihan - 1]
        logging.info(f"📝 Tema dipilih: {tema_terpilih}")
    except (ValueError, IndexError):
        logging.error("❌ Pilihan tidak valid.")
        return

    # Ambil data kegiatan
    tema_data = data["klasifikasi_tema"][tema_terpilih]

    # Buat hasil analisis
    hasil = {
        "tema": tema_terpilih,
        "jumlah_kegiatan": len(tema_data),
        "kegiatan": tema_data
    }

    # Simpan ke JSON
    output_path = os.path.join(OUTPUT_FOLDER, f"hasil_tema_{tema_terpilih}.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hasil, f, indent=4, ensure_ascii=False)
        logging.info(f"📂 Hasil analisis tema '{tema_terpilih}' disimpan ke: {output_path}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan file: {e}")
        return

    logging.info("🎉 Analisis selesai.")

if __name__ == "__main__":
    analisis_tema()
