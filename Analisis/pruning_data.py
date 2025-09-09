import json
import os
import sys
import logging
from collections import Counter

# --- SETUP LOGGING ---
OUTPUT_DIR = "Output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, "proses.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Path file input (pakai full path biar pasti kebaca)
INPUT_FILE = r"D:\testing magang\Analisis_isu_PythonFile-main\Data\data_klasifikasi.json"

# Load data JSON
try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    logging.info(f"✅ File {INPUT_FILE} berhasil dimuat.")
except FileNotFoundError:
    logging.error(f"❌ File {INPUT_FILE} tidak ditemukan.")
    sys.exit()
except json.JSONDecodeError:
    logging.error(f"❌ File {INPUT_FILE} bukan JSON valid.")
    sys.exit()

# Ambil semua tema
all_themes = list(data.get("klasifikasi_tema", {}).keys())
if not all_themes:
    logging.warning("⚠️ Tidak ada tema ditemukan di file JSON.")
    sys.exit()

logging.info("📌 Daftar Tema:")
for idx, tema in enumerate(all_themes, start=1):
    logging.info(f"{idx}. {tema}")

# Pilih tema
try:
    pilihan = int(input("\nPilih nomor tema: "))
    tema_terpilih = all_themes[pilihan - 1]
    logging.info(f"📝 Tema dipilih: {tema_terpilih}")
except (ValueError, IndexError):
    logging.error("❌ Pilihan tidak valid.")
    sys.exit()

# Ambil kegiatan di tema terpilih
activities = data["klasifikasi_tema"][tema_terpilih]

logging.info("\n🔧 Pilih mode pruning:")
logging.info("1. Hapus duplikat kegiatan")
logging.info("2. Filter berdasarkan keyword")
logging.info("3. Ambil top-N kegiatan terbanyak")
mode = input("Masukkan pilihan (1/2/3): ").strip()

pruned = []

# Mode 1: Hapus duplikat
if mode == "1":
    seen = {}
    for item in activities:
        seen[item["namakegiatan"]] = item
    pruned = list(seen.values())
    logging.info(f"✅ {len(activities) - len(pruned)} duplikat dihapus. Total akhir: {len(pruned)} kegiatan.")

# Mode 2: Filter keyword
elif mode == "2":
    keyword = input("Masukkan keyword: ").lower()
    pruned = [item for item in activities if keyword in item["namakegiatan"].lower()]
    logging.info(f"✅ Ditemukan {len(pruned)} kegiatan dengan keyword '{keyword}'.")

# Mode 3: Top-N
elif mode == "3":
    try:
        N = int(input("Masukkan jumlah top-N: "))
    except ValueError:
        logging.error("❌ Input N tidak valid.")
        sys.exit()
    counter = Counter(item["namakegiatan"] for item in activities)
    topN = counter.most_common(N)
    pruned = [item for item in activities if item["namakegiatan"] in dict(topN)]
    logging.info(f"✅ Diambil {len(pruned)} kegiatan teratas dari total {len(activities)}.")
else:
    logging.error("❌ Mode tidak valid.")
    sys.exit()

# Simpan hasil
output_file = os.path.join(OUTPUT_DIR, f"hasil_pruning_{tema_terpilih}.json")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2, ensure_ascii=False)
    logging.info(f"📂 Hasil pruning disimpan di: {output_file}")
except Exception as e:
    logging.error(f"❌ Gagal menyimpan file: {e}")
    sys.exit()

logging.info("🎉 Proses pruning selesai.")
