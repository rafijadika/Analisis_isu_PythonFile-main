import json
import os
import re
from collections import Counter

# Path input/output
INPUT_FILE = r"D:\testing magang\Analisis_isu_PythonFile-main\Data\data_pemda.json"
OUTPUT_FILE = r"D:\testing magang\Analisis_isu_PythonFile-main\Output\kamus_tema.json"

# Stopwords diperluas (non teknis)
stopwords = {
    "dan","yang","untuk","dengan","dalam","pada","dari","ke","di","atau",
    "agar","serta","sebagai","juga","bagi","adalah","akan","masih","sudah",
    "dapat","lebih","kurang","hingga","oleh","sehingga","yaitu","yakni",
    "antara","lain","diharapkan","perlu","pernah","akan","tetapi","merupakan",
    "dalam","rangka","supaya","bukan","dimana","adapun","terhadap","oleh karena itu"
}

# Sinonim → bentuk standar
synonyms = {
    "perekonomian": "ekonomi", "ekonomi": "ekonomi",
    "edukasi": "pendidikan", "pendidikan": "pendidikan",
    "sarana": "infrastruktur", "prasarana": "infrastruktur",
    "sarana prasarana": "infrastruktur",
    "lingkungan": "lingkungan", "ekologi": "lingkungan",
    "kesehatan": "kesehatan", "medis": "kesehatan",
    "kebudayaan": "budaya", "budaya": "budaya",
    "transportasi": "transportasi", "jalan": "transportasi",
    "energi": "energi",
    "digitalisasi": "digital", "teknologi": "teknologi",
    "informatika": "teknologi", "komputer": "teknologi",
    "umkm": "umkm", "usaha": "umkm"
}

# Whitelist kata teknis (tema besar)
whitelist = {
    "ekonomi","perdagangan","umkm","industri","pajak","fiskal",
    "pendidikan","literasi","sdm","pemuda","karakter",
    "kesehatan","gizi","stunting","rumah sakit",
    "lingkungan","sampah","konservasi","bencana","iklim",
    "infrastruktur","transportasi","hunian","kota","drainase",
    "tata kelola","pemerintahan","birokrasi","regulasi","asn",
    "budaya","masyarakat","keberagaman","pariwisata","sosial",
    "teknologi","digital","inovasi","platform","industri 4.0",
    "keamanan","hukum","ham","narkoba","kriminalitas","energi"
}

# Tema besar
common_themes = {
    "Ekonomi": ["ekonomi","perdagangan","investasi","umkm","industri","pajak","fiskal"],
    "SDM & Pendidikan": ["pendidikan","literasi","sdm","generasi","pemuda","karakter"],
    "Kesehatan": ["kesehatan","gizi","stunting","rumah sakit","layanan"],
    "Lingkungan & Bencana": ["lingkungan","sampah","konservasi","bencana","iklim"],
    "Infrastruktur & Kota": ["infrastruktur","transportasi","hunian","kota","drainase"],
    "Tata Kelola & Birokrasi": ["tata kelola","pemerintahan","birokrasi","regulasi","asn"],
    "Sosial & Budaya": ["budaya","masyarakat","keberagaman","pariwisata","sosial"],
    "Teknologi & Digitalisasi": ["teknologi","digital","inovasi","platform","industri 4.0"],
    "Keamanan & Hukum": ["keamanan","hukum","ham","narkoba","kriminalitas"]
}

def clean_token(token):
    token = token.lower()
    token = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", "", token)
    token = token.strip()
    if token in synonyms:
        token = synonyms[token]
    return token

# Load data
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

data = raw.get("data", raw)

# Ambil semua isu
all_tokens = []
for item in data:
    isu_list = item.get("data", [])
    if isinstance(isu_list, list):
        for isu in isu_list:
            if isinstance(isu, str):
                tokens = [clean_token(t) for t in isu.split()]
                tokens = [
                    t for t in tokens
                    if t and t not in stopwords and len(t) > 2 and t in whitelist
                ]
                all_tokens.extend(tokens)

# Hitung frekuensi
counter = Counter(all_tokens)
filtered_keywords = {k for k, v in counter.items() if v >= 2}

# Mapping ke tema
themes_output = []
for idx, (theme, keywords) in enumerate(common_themes.items(), start=1):
    mapped = [kw for kw in keywords if kw in filtered_keywords]
    if mapped:
        themes_output.append({
            "id": f"theme-{idx}",
            "name": theme,
            "keywords": mapped,
            "color": ["#3b82f6","#10b981","#ef4444","#f59e0b","#8b5cf6","#06b6d4"][idx % 6]
        })

output = {
    "allKeywords": sorted(filtered_keywords),
    "themes": themes_output
}

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Hasil pruning tema tersimpan di {OUTPUT_FILE}")
