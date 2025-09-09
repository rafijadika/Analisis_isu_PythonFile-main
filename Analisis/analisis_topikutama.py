import json
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
import logging

# --- SETUP LOGGING ---
os.makedirs("./Output", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("./Output/proses.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# LOAD KAMUS TEMA ===
kamus_path = "Data/kamus_tema.json"
try:
    with open(kamus_path, "r", encoding="utf-8") as f:
        kamus_data = json.load(f)
    logging.info(f"✅ File {kamus_path} berhasil dimuat.")
except FileNotFoundError:
    logging.error(f"❌ File {kamus_path} tidak ditemukan.")
    sys.exit()
except json.JSONDecodeError:
    logging.error(f"❌ File {kamus_path} bukan JSON yang valid.")
    sys.exit()

if "klasifikasi_topik" not in kamus_data:
    logging.error("❌ Struktur JSON tidak sesuai, key 'klasifikasi_topik' tidak ditemukan.")
    sys.exit()

# THEMES { "Ekonomi": ["ekonomi", "perdagangan", dll]}
THEMES = {item["nama"]: item["keywords"] for item in kamus_data["klasifikasi_topik"]}

# FUNGSI CLEANING TEKS 
def clean_issue(issue_text: str):
    """Membersihkan teks isu agar lebih siap untuk analisis TF-IDF."""
    return re.sub(r'^[a-z0-9\.\-)\s]+', '', issue_text.lower().strip())

# ANALISIS SATU PEMDA 
def analyze_single_region_issues_tfidf(pemda_data, threshold=0.25):
    issues = pemda_data.get('data', [])
    if not issues or not issues[0]:
        return None, None, None, None

    theme_counts = Counter()
    theme_scores = {theme: [] for theme in THEMES}
    matched_issues_by_theme = {theme: [] for theme in THEMES}
    unmatched_issues = []

    # Gabungkan keyword tiap tema jadi satu teks
    theme_representations = {theme: " ".join(keywords) for theme, keywords in THEMES.items()}
    vectorizer = TfidfVectorizer()

    for issue in issues:
        cleaned_issue = clean_issue(issue)
        if not cleaned_issue:
            continue

        best_theme = None
        best_score = 0

        # Bandingin dengan semua tema
        for theme, theme_text in theme_representations.items():
            tfidf_matrix = vectorizer.fit_transform([cleaned_issue, theme_text])
            score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            if score > best_score:
                best_score = score
                best_theme = theme

        # Threshold supaya gak asal cocok
        if best_score >= threshold and best_theme:
            theme_counts[best_theme] += 1
            theme_scores[best_theme].append(round(best_score * 100, 2))
            matched_issues_by_theme[best_theme].append(issue.strip())
        else:
            unmatched_issues.append(issue.strip())

    return theme_counts, unmatched_issues, matched_issues_by_theme, theme_scores

# LOAD DATA PEMDA 
data_path = "Data/data_pemda.json"
try:
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)["data"]
    logging.info(f"✅ File {data_path} berhasil dimuat. Jumlah pemda: {len(data)}")
except FileNotFoundError:
    logging.error(f"❌ File {data_path} tidak ditemukan.")
    sys.exit()
except json.JSONDecodeError:
    logging.error(f"❌ File {data_path} bukan JSON yang valid.")
    sys.exit()

hasil_akhir = []

for pemda in data:
    theme_counts, unmatched, matched, scores = analyze_single_region_issues_tfidf(pemda)
    if not theme_counts:
        continue

    top_themes = theme_counts.most_common(2)  
    hasil_akhir.append({
        "pemda": pemda["namapemda"],
        "top_themes": top_themes,
        "matched_issues": matched,
        "scores": scores,
        "unmatched_issues": unmatched
    })
    logging.info(f"📊 {pemda['namapemda']} dianalisis. Top tema: {top_themes}")

# SIMPAN HASIL 
output_path = "./Output/hasil_topikutama.json"
try:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hasil_akhir, f, ensure_ascii=False, indent=2)
    logging.info(f"📂 Hasil analisis tersimpan di '{output_path}'")
except Exception as e:
    logging.error(f"❌ Gagal menyimpan file: {e}")
    sys.exit()

logging.info("🎉 Analisis selesai.")
