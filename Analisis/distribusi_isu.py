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
os.makedirs("Output", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("Output/proses.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Path file input/output
input_path = Path(r"D:\testing magang\Analisis_isu_PythonFile-main\Data\data_pemda.json")
output_path = Path("Output/distribusi_isu.html")

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

# Kumpulkan semua isu ke satu list dengan normalisasi
all_issues = []
for item in data:
    isu = item.get("data", [])
    if isinstance(isu, list):
        for i in isu:
            if isinstance(i, dict):  # kalau format dict
                val = str(i.get("kategori", "")).strip().lower()
                if val:
                    all_issues.append(val)
            elif isinstance(i, str):  # kalau format string
                all_issues.append(i.strip().lower())
    elif isinstance(isu, str):
        all_issues.append(isu.strip().lower())

logging.info(f"📊 Total isu terkumpul: {len(all_issues)}")

# Hitung distribusi isu
counter = Counter(all_issues)
logging.info(f"📈 Jumlah kategori isu ditemukan: {len(counter)}")

# Buat DataFrame untuk distribusi
df = pd.DataFrame(counter.items(), columns=["Isu", "Jumlah"]).sort_values(by="Jumlah", ascending=False)

# Logging 10 besar isu
logging.info("🏆 10 Isu Teratas:")
for isu, jumlah in counter.most_common(10):
    logging.info(f"   - {isu}: {jumlah}")

# --- Buat grafik batang ---
plt.figure(figsize=(10, 6))
df.head(10).plot(kind="bar", x="Isu", y="Jumlah", legend=False, color="skyblue")
plt.title("Top 10 Distribusi Isu Strategis")
plt.xlabel("Isu")
plt.ylabel("Jumlah")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Simpan grafik ke memory buffer
buf = BytesIO()
plt.savefig(buf, format="png", bbox_inches="tight")
plt.close()
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode("utf-8")

# Generate tabel HTML
table_html = df.to_html(index=False, escape=False)

# Bungkus dengan template HTML + grafik
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
  h1 {{
    margin-bottom: 10px;
    font-size: 24px;
  }}
  .sub {{
    color: #9ca3af;
    margin-bottom: 20px;
    font-size: 14px;
  }}
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
    vertical-align: top;
  }}
  th {{
    background: #1e293b;
    color: #93c5fd;
    position: sticky;
    top: 0;
  }}
  tr:nth-child(odd) {{
    background: rgba(255,255,255,0.02);
  }}
  .chart {{
    margin: 20px 0;
    text-align: center;
  }}
  img {{
    max-width: 100%;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.5);
  }}
</style>
</head>
<body>
  <h1>Distribusi Isu Strategis</h1>
  <div class="sub">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • Total isu unik: {len(counter)}</div>
  
  <div class="chart">
    <h2>Top 10 Isu</h2>
    <img src="data:image/png;base64,{img_base64}" alt="Grafik Distribusi Isu"/>
  </div>
  
  {table_html}
</body>
</html>"""

# Simpan ke file
try:
    output_path.write_text(html, encoding="utf-8")
    logging.info(f"📂 Tabel + grafik distribusi isu berhasil diekspor ke: {output_path}")
except Exception as e:
    logging.error(f"❌ Gagal menyimpan file HTML: {e}")
    sys.exit()

logging.info("🎉 Proses analisis distribusi isu selesai.")
