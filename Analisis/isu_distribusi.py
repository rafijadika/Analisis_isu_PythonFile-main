import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import sys
import os
from collections import Counter
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# --- SETUP LOGGING ---
output_dir = Path(r"D:\testing magang\Analisis_isu_PythonFile-main\Output")
output_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(output_dir / "proses.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- KAMUS TEMA ISU STRATEGIS ---
common_themes = {
    "Ekonomi": [
        "ekonomi", "ekonomi kreatif", "pertumbuhan ekonomi", "perdagangan",
        "kemiskinan", "umkm", "investasi", "fiskal", "pajak", "hilirisasi",
        "agrobisnis", "pendapatan", "kewirausahaan", "kemandirian daerah"
    ],
    "SDM": [
        "sumber daya manusia", "sdm", "pengembangan sumber daya manusia", "tenaga kerja",
        "kualitas sdm", "human capital", "adaptif", "generasi emas", "pemuda", "modal manusia"
    ],
    "Pendidikan": [
        "pendidikan", "sekolah", "literasi", "kurikulum",
        "akses pendidikan", "mutu pendidikan", "vokasi"
    ],
    "Kesehatan": [
        "kesehatan", "fasilitas kesehatan", "rumah sakit",
        "gizi", "epidemi", "layanan kesehatan"
    ],
    "Stunting": ["stunting"],
    "Lapangan Pekerjaan": [
        "lapangan pekerjaan", "pekerjaan", "kesempatan kerja",
        "pengangguran", "serapan tenaga kerja"
    ],
    "Infrastruktur dan Utilitas Kota": [
        "infrastruktur", "utilitas", "sarana prasarana", "fasilitas umum",
        "konektivitas", "transportasi", "permukiman", "drainase",
        "aksesibilitas", "hunian"
    ],
    "Tata Ruang & Perkotaan": [
        "tata ruang", "penataan ruang", "kewilayahan", "perkotaan",
        "urbanisasi", "urban sprawl", "pemukiman", "kota"
    ],
    "Lingkungan Hidup": [
        "lingkungan", "lingkungan hidup", "pencemaran", "konservasi",
        "ketahanan lingkungan", "ekologi"
    ],
    "Bencana": [
        "bencana", "kebencanaan", "mitigasi", "adaptasi iklim", "risiko bencana"
    ],
    "Tata Kelola Pemerintahan": [
        "tata kelola", "pemerintahan", "good governance", "transparan",
        "akuntabel", "regulasi", "inovasi birokrasi", "kolaboratif", "asn",
        "partisipasi publik"
    ],
    "Birokrasi": ["birokrasi", "reformasi birokrasi"],
    "Sosial Budaya": [
        "sosial", "budaya", "kebudayaan", "ketertiban", "masyarakat",
        "demografi", "kearifan lokal", "lgbt", "miras", "judi",
        "pmks", "kriminalitas"
    ],
    "Gender": ["gender"],
    "Hak Anak": ["hak anak", "anak"],
    "Keamanan": ["keamanan"],
    "Agama": ["agama"],
    "Hukum dan HAM": ["hukum", "hak asasi manusia", "ham"],
    "Digitalisasi & Teknologi": [
        "digital", "teknologi", "inovasi", "disrupsi", "platform",
        "literasi digital", "industri 4.0", "transformasi digital"
    ],
    "IKN": ["ikn", "ibu kota negara", "pemindahan ibu kota"],
    "Kota Cerdas": ["kota cerdas", "smart city", "teknologi kota"],
    "Citra Kota": ["citra kota", "branding kota", "identitas kota"],
    "Kota Jasa": ["kota jasa", "sektor jasa"],
    "Pangan": ["pangan", "ketahanan pangan"],
    "Pemerataan Pembangunan": ["pemerataan", "pembangunan merata"],
    "Revitalisasi Sungai": ["sungai", "revitalisasi sungai"],
    "MICE": ["mice", "event", "konferensi"],
    "Fiskal Daerah": ["fiskal", "keuangan daerah", "pendapatan daerah"],
    "Transportasi": ["transportasi", "mobilitas", "lalu lintas"],
    "Iklim Global": ["iklim global", "perubahan iklim"],
    "Pariwisata": ["pariwisata", "wisata"],
    "Kebijakan Daerah": ["kebijakan daerah", "perda"],
    "SDA": ["sumber daya alam", "sda", "sumber daya alam"],
    "Energi terbarukan": ["energi terbarukan", "energi hijau"],
    "Megatrend Global": ["megatrend", "globalisasi"],
    "Urbanisasi": ["urbanisasi", "perkembangan kota"],
    "Geopolitik global": ["geopolitik", "politik global"],
    "Produktivitas Nasional": ["produktivitas", "nasional"],
    "Kesejahteraan Masyarakat": ["kesejahteraan", "masyarakat sejahtera"],
    "Sampah": ["sampah", "pengelolaan sampah"],
    "Sanitasi": ["sanitasi", "kebersihan"],
    "MKM": ["mkm", "usaha kecil", "mikro"],
    "Pertanian": ["pertanian", "petani"],
    "Industrialisasi": ["industrialisasi", "pabrik"],
    "Pelayanan Publik": ["pelayanan publik", "layanan masyarakat"],
    "Air bersih": ["air bersih", "akses air"],
    "Tenaga Kerja Asing": ["tenaga kerja asing", "tka"],
    "Sustainable Development Goals (SDG's)": [
        "sustainable development goals", "sdgs", "sdg"
    ],
    "Narkoba": ["narkoba"]
}

# Path file input/output
input_path = Path(r"D:\testing magang\Analisis_isu_PythonFile-main\Data\data_pemda.json")
html_path = output_dir / "distribusi_isu.html"
excel_path = output_dir / "distribusi_isu.xlsx"

# Load JSON
try:
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    logging.info(f"✅ File {input_path} berhasil dimuat.")
except FileNotFoundError:
    logging.error(f"❌ File {input_path} tidak ditemukan.")
    sys.exit()
except json.JSONDecodeError:
    logging.error(f"❌ File {input_path} bukan JSON yang valid.")
    sys.exit()

# Ambil bagian data aja
data = raw.get("data", raw)

# Kumpulkan semua isu
all_issues = []
for item in data:
    isu = item.get("data", [])
    if isinstance(isu, list):
        for i in isu:
            if isinstance(i, dict):
                val = str(i.get("kategori", "")).strip().lower()
                if val:
                    all_issues.append(val)
            elif isinstance(i, str):
                all_issues.append(i.strip().lower())
    elif isinstance(isu, str):
        all_issues.append(isu.strip().lower())

logging.info(f"📊 Total isu terkumpul: {len(all_issues)}")

# --- Mapping isu ke tema ---
mapped = []
for isu in all_issues:
    found = False
    for tema, keywords in common_themes.items():
        if any(k in isu for k in keywords):
            mapped.append(tema)
            found = True
            break
    if not found:
        mapped.append("Lainnya")

counter = Counter(mapped)
df = pd.DataFrame(counter.items(), columns=["Tema", "Jumlah"]).sort_values(by="Jumlah", ascending=False)

# --- Simpan ke Excel ---
df.to_excel(excel_path, index=False, engine="openpyxl")
logging.info(f"📂 Hasil distribusi isu juga disimpan di {excel_path}")

# --- Grafik ---
plt.figure(figsize=(10, 6))
df.head(10).plot(kind="bar", x="Tema", y="Jumlah", legend=False, color="skyblue")
plt.title("Top 10 Distribusi Isu Strategis (Tema)")
plt.xlabel("Tema")
plt.ylabel("Jumlah")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

buf = BytesIO()
plt.savefig(buf, format="png", bbox_inches="tight")
plt.close()
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode("utf-8")

# --- HTML ---
table_html = df.to_html(index=False, escape=False)

html = f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Distribusi Isu Strategis</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    background: #0b1220;
    color: #e5e7eb;
    padding: 32px;
  }}
  h1 {{ font-size: 24px; margin-bottom: 10px; }}
  .sub {{ color: #9ca3af; margin-bottom: 20px; font-size: 14px; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    background: #111827;
    border-radius: 12px;
    overflow: hidden;
  }}
  th, td {{
    border: 1px solid #1f2937;
    padding: 10px 14px;
    text-align: left;
  }}
  th {{ background: #1e293b; color: #93c5fd; position: sticky; top: 0; }}
  tr:nth-child(odd) {{ background: rgba(255,255,255,0.02); }}
  .chart {{ margin: 20px 0; text-align: center; }}
  img {{ max-width: 100%; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.5); }}
</style>
</head>
<body>
  <h1>Distribusi Isu Strategis</h1>
  <div class="sub">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • Total tema unik: {len(counter)}</div>
  
  <div class="chart">
    <h2>Top 10 Tema</h2>
    <img src="data:image/png;base64,{img_base64}" alt="Grafik Distribusi Isu"/>
  </div>
  
  {table_html}
</body>
</html>"""

html_path.write_text(html, encoding="utf-8")
logging.info(f"📂 Hasil distribusi isu berdasarkan tema disimpan di {html_path}")
