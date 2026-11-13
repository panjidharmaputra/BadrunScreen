import os
import json
import threading
import webbrowser
import csv
from collections import Counter
from flask import Flask, render_template, request, jsonify
from engine.hybrid_engine import HybridEngine

app = Flask(__name__)

# Konfigurasi Path dan Engine
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data")
engine = HybridEngine(data_path)

# ============================================================
# SOLUSI & TIPS DETAIL PER PENYAKIT
# ============================================================
DETAILED_SOLUTIONS = {
    "P01": {
        "first_aid": [
            "Istirahat total di tempat tidur (bed rest)",
            "Perbanyak minum air putih, jus buah, atau oralit (minimal 2-3 liter/hari)",
            "Konsumsi Paracetamol untuk menurunkan demam (JANGAN aspirin/ibuprofen)",
            "Kompres hangat pada dahi dan ketiak"
        ],
        "diet": [
            "Makan bubur/nasi lembek agar mudah dicerna",
            "Konsumsi buah kaya vitamin C (jambu biji, jeruk, pepaya)",
            "Hindari makanan berminyak dan pedas",
            "Minum jus jambu biji merah (membantu menaikkan trombosit)"
        ],
        "when_to_hospital": [
            "Mimisan atau gusi berdarah yang tidak berhenti",
            "Muntah terus-menerus",
            "Nyeri perut hebat",
            "Kulit dingin, lembab, dan pucat (tanda syok)",
            "Trombosit turun di bawah 100.000"
        ],
        "prevention": [
            "Lakukan 3M Plus: Menguras, Menutup, Mengubur + gunakan lotion anti nyamuk",
            "Pasang kelambu saat tidur",
            "Gunakan obat nyamuk atau fogging berkala",
            "Hindari genangan air di sekitar rumah"
        ],
        "medication": [
            "Paracetamol — penurun demam (dosis sesuai kemasan/anjuran apoteker)",
            "Oralit — mengganti cairan tubuh saat demam/muntah",
            "JANGAN konsumsi Aspirin atau Ibuprofen (risiko perdarahan pada DBD)"
        ]
    },
    "P02": {
        "first_aid": [
            "Istirahat yang cukup (7-9 jam/hari)",
            "Minum air hangat secukupnya",
            "Konsumsi Paracetamol jika demam di atas 38°C",
            "Kumur air garam hangat untuk meredakan sakit tenggorokan"
        ],
        "diet": [
            "Makan sup ayam hangat (membantu melegakan hidung tersumbat)",
            "Konsumsi buah-buahan kaya vitamin C dan zinc",
            "Minum teh hangat dengan madu dan lemon",
            "Hindari makanan dingin dan minuman es"
        ],
        "when_to_hospital": [
            "Demam tidak turun setelah 3 hari",
            "Sesak napas atau nyeri dada",
            "Batuk berdahak berwarna hijau/kuning pekat",
            "Kebingungan atau penurunan kesadaran"
        ],
        "prevention": [
            "Vaksinasi flu tahunan",
            "Cuci tangan dengan sabun secara rutin",
            "Gunakan masker saat di tempat ramai",
            "Hindari menyentuh wajah dengan tangan kotor"
        ],
        "medication": [
            "Paracetamol — jika demam di atas 38°C",
            "Dekongestan (mis. pseudoefedrin) — melegakan hidung tersumbat",
            "Antihistamin — jika pilek berair dan bersin-bersin"
        ]
    },
    "P03": {
        "first_aid": [
            "Istirahat total dan tidak beraktivitas berat",
            "Minum air putih yang banyak untuk mencegah dehidrasi",
            "Konsumsi Paracetamol untuk demam",
            "Segera ke dokter untuk mendapatkan antibiotik (Kloramfenikol/Ciprofloxacin)"
        ],
        "diet": [
            "Makan makanan lunak: bubur, nasi tim, roti lembut",
            "Hindari makanan pedas, asam, dan berminyak",
            "Makan dalam porsi kecil tapi sering",
            "Hindari susu dan produk olahan susu sementara"
        ],
        "when_to_hospital": [
            "Demam tidak turun meskipun sudah minum antibiotik 3 hari",
            "BAB berdarah",
            "Perut kembung keras dan nyeri hebat",
            "Penurunan kesadaran"
        ],
        "prevention": [
            "Cuci tangan sebelum makan dan setelah dari toilet",
            "Makan makanan yang dimasak matang sempurna",
            "Minum air yang sudah dimasak/steril",
            "Vaksinasi tifoid jika sering bepergian"
        ],
        "medication": [
            "Antibiotik (Kloramfenikol/Ciprofloxacin) — HANYA dengan resep dokter",
            "Paracetamol — penurun demam",
            "Oralit — mencegah dehidrasi akibat demam/diare"
        ]
    },
    "P04": {
        "first_aid": [
            "Istirahat dan kurangi aktivitas berat",
            "Minum air hangat secara rutin",
            "Hirup uap air hangat (steam inhalation) untuk melegakan napas",
            "Gunakan obat batuk sesuai jenis (kering/berdahak)"
        ],
        "diet": [
            "Konsumsi makanan hangat dan bergizi",
            "Minum teh hangat dengan madu",
            "Makan buah kaya vitamin C dan E",
            "Hindari gorengan dan makanan yang memicu batuk"
        ],
        "when_to_hospital": [
            "Sesak napas yang tidak membaik",
            "Batuk lebih dari 2 minggu",
            "Demam tinggi berkepanjangan",
            "Dahak bercampur darah"
        ],
        "prevention": [
            "Gunakan masker di tempat berdebu/ramai",
            "Hindari asap rokok (aktif maupun pasif)",
            "Jaga kebersihan lingkungan rumah",
            "Rutin berolahraga untuk menjaga daya tahan tubuh"
        ],
        "medication": [
            "Obat batuk kering (dekstrometorfan) atau batuk berdahak (guaifenesin) — pilih sesuai jenis batuk",
            "Paracetamol — jika disertai demam",
            "Pelega tenggorokan (lozenges) — untuk sakit tenggorokan"
        ]
    },
    "P05": {
        "first_aid": [
            "Segera cek gula darah puasa di lab/klinik",
            "Kurangi konsumsi gula dan karbohidrat sederhana",
            "Perbanyak minum air putih",
            "Catat semua gejala untuk dilaporkan ke dokter"
        ],
        "diet": [
            "Pilih karbohidrat kompleks: nasi merah, oat, ubi",
            "Perbanyak sayuran hijau dan serat",
            "Hindari minuman manis dan jus kemasan",
            "Makan teratur dengan jadwal tetap"
        ],
        "when_to_hospital": [
            "Gula darah puasa di atas 200 mg/dL",
            "Penurunan berat badan drastis tanpa sebab",
            "Luka yang tidak kunjung sembuh",
            "Penglihatan kabur tiba-tiba"
        ],
        "prevention": [
            "Olahraga teratur minimal 150 menit/minggu",
            "Jaga berat badan ideal (BMI 18.5-24.9)",
            "Cek gula darah rutin setiap 6 bulan",
            "Kelola stres dengan baik"
        ],
        "medication": [
            "TIDAK ada obat bebas untuk diabetes — wajib konsultasi dokter",
            "Obat diabetes (mis. metformin) hanya boleh dipakai dengan resep dokter",
            "Fokus pada pengaturan pola makan dan olahraga teratur"
        ]
    },
    "P06": {
        "first_aid": [
            "Isolasi mandiri di ruangan terpisah",
            "Gunakan masker N95/KN95 di dalam rumah",
            "Konsumsi Paracetamol untuk demam",
            "Lakukan tes Swab Antigen/PCR sesegera mungkin"
        ],
        "diet": [
            "Makan makanan bergizi tinggi protein (telur, ikan, ayam)",
            "Konsumsi vitamin C, D, dan Zinc",
            "Minum air hangat secukupnya (8+ gelas/hari)",
            "Makan buah-buahan segar"
        ],
        "when_to_hospital": [
            "Saturasi oksigen di bawah 95% (SpO2 < 95)",
            "Sesak napas berat dan tidak membaik",
            "Nyeri dada yang persisten",
            "Bibir atau wajah membiru (sianosis)"
        ],
        "prevention": [
            "Vaksinasi COVID-19 dan booster",
            "Cuci tangan dengan sabun 20 detik",
            "Jaga jarak fisik minimal 1 meter",
            "Hindari kerumunan di tempat tertutup"
        ],
        "medication": [
            "Paracetamol — penurun demam dan pereda nyeri",
            "Vitamin C, D, dan Zinc — mendukung daya tahan tubuh",
            "Obat batuk sesuai jenis batuk yang dialami"
        ]
    },
    "P07": {
        "first_aid": [
            "Makan dalam porsi kecil tapi sering (5-6x sehari)",
            "Hindari berbaring setelah makan (tunggu 2-3 jam)",
            "Konsumsi antasida untuk meredakan nyeri lambung",
            "Hindari stres berlebihan"
        ],
        "diet": [
            "Makan nasi, roti, dan makanan rendah asam",
            "Hindari makanan pedas, asam, berlemak, dan berkafein",
            "Hindari alkohol dan minuman bersoda",
            "Konsumsi oatmeal, pisang, dan yogurt rendah lemak"
        ],
        "when_to_hospital": [
            "Muntah darah atau BAB berwarna hitam",
            "Nyeri perut yang sangat hebat dan tidak tertahankan",
            "Penurunan berat badan drastis",
            "Sulit menelan yang semakin memburuk"
        ],
        "prevention": [
            "Makan teratur dan jangan melewatkan waktu makan",
            "Kelola stres (meditasi, olahraga ringan)",
            "Hindari makan terlalu cepat, kunyah makanan dengan baik",
            "Tidur cukup dan teratur (7-8 jam/hari)"
        ],
        "medication": [
            "Antasida — menetralkan asam lambung (mis. yang mengandung aluminium/magnesium hidroksida)",
            "Obat golongan PPI (mis. omeprazole) — konsultasikan dulu ke apoteker",
            "Hindari NSAID (aspirin, ibuprofen) karena mengiritasi lambung"
        ]
    }
}

MEDICATION_DISCLAIMER = (
    "Daftar obat di atas adalah golongan obat bebas/bebas terbatas yang umum. "
    "Selalu baca aturan pakai pada kemasan dan konsultasikan ke apoteker atau dokter "
    "sebelum mengonsumsi — terutama jika Anda punya riwayat alergi, sedang hamil/menyusui, "
    "atau mengonsumsi obat lain."
)


def get_dataset_stats():
    """Menghitung statistik dari dataset CSV"""
    csv_path = os.path.join(data_path, "dataset.csv")
    stats = {
        "total_samples": 0,
        "total_features": 0,
        "total_classes": 0,
        "class_distribution": {},
        "avg_symptoms_per_sample": 0,
        "feature_frequency": {}
    }
    
    if not os.path.exists(csv_path):
        return stats
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return stats
        
        feature_cols = [col for col in rows[0].keys() if col != "Target"]
        stats["total_features"] = len(feature_cols)
        stats["total_samples"] = len(rows)
        
        targets = [row["Target"] for row in rows]
        stats["class_distribution"] = dict(Counter(targets))
        stats["total_classes"] = len(stats["class_distribution"])
        
        # Rata-rata gejala per sampel
        total_symptoms = 0
        feature_counts = Counter()
        for row in rows:
            sample_symptoms = sum(1 for col in feature_cols if row[col].strip() == "1")
            total_symptoms += sample_symptoms
            for col in feature_cols:
                if row[col].strip() == "1":
                    feature_counts[col] += 1
        
        stats["avg_symptoms_per_sample"] = round(total_symptoms / len(rows), 1) if rows else 0
        stats["feature_frequency"] = dict(feature_counts.most_common())
        
    except Exception as e:
        print(f"Error reading dataset stats: {e}")
    
    return stats


@app.route('/')
def index():
    with open(os.path.join(data_path, "symptoms.json"), "r") as f:
        symptoms = json.load(f)
    with open(os.path.join(data_path, "diseases.json"), "r") as f:
        diseases = json.load(f)
    with open(os.path.join(data_path, "rules.json"), "r") as f:
        rules = json.load(f)
    
    dataset_stats = get_dataset_stats()
    model_accuracy = getattr(engine.ml, "accuracy", None)
    
    return render_template('index.html',
        symptoms=symptoms,
        diseases=diseases,
        rules=rules,
        dataset_stats=dataset_stats,
        model_accuracy=model_accuracy
    )


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    selected_symptoms = data.get('symptoms', [])
    
    if not selected_symptoms:
        return jsonify({"error": "Tidak ada gejala yang dipilih"})
    
    results, forward_trace, backward_proofs = engine.process_screening(selected_symptoms)
    
    with open(os.path.join(data_path, "diseases.json"), "r") as f:
        diseases = json.load(f)
    with open(os.path.join(data_path, "symptoms.json"), "r") as f:
        symptoms = json.load(f)
    
    if results:
        # Kirim SEMUA hasil, tidak hanya yang pertama
        all_results = []
        for r in results:
            disease_info = diseases[r["disease_id"]]
            solution = DETAILED_SOLUTIONS.get(r["disease_id"], {})
            
            matched_names = [symptoms.get(s, s) for s in r.get("matched_symptoms", [])]
            missing_names = [symptoms.get(s, s) for s in r.get("missing_symptoms", [])]
            
            all_results.append({
                "disease_id": r["disease_id"],
                "disease_name": disease_info["name"],
                "confidence": r["hybrid_confidence"],
                "expert_confidence": r.get("expert_confidence"),
                "forward_confidence": r.get("forward_confidence"),
                "backward_confidence": r.get("backward_confidence"),
                "backward_verified": r.get("backward_verified", False),
                "ml_supported": r.get("ml_supported", False),
                "ml_probability": r.get("ml_probability"),
                "recommendation": disease_info["recommendation"],
                "red_flag": disease_info["red_flag"],
                "matched_symptoms": matched_names,
                "missing_symptoms": missing_names,
                "matched_count": len(r.get("matched_symptoms", [])),
                "total_conditions": len(r.get("matched_symptoms", [])) + len(r.get("missing_symptoms", [])),
                "first_aid": solution.get("first_aid", []),
                "diet": solution.get("diet", []),
                "medication": solution.get("medication", []),
                "medication_disclaimer": MEDICATION_DISCLAIMER,
                "when_to_hospital": solution.get("when_to_hospital", []),
                "prevention": solution.get("prevention", [])
            })
        
        return jsonify({
            "results": all_results,
            "selected_count": len(selected_symptoms),
            "total_candidates": len(all_results),
            "reasoning": {
                "forward_trace": forward_trace,
                "backward_proofs": backward_proofs,
            }
        })
    else:
        return jsonify({"error": "Pola gejala tidak dikenali oleh sistem."})


@app.route('/backward_chaining', methods=['POST'])
def backward_chaining():
    data = request.json
    disease_id = data.get('disease_id')
    user_symptoms = data.get('symptoms', [])
    
    bc = engine.expert.backward_chaining(disease_id, user_symptoms)

    with open(os.path.join(data_path, "symptoms.json"), "r") as f:
        symptoms_dict = json.load(f)
    with open(os.path.join(data_path, "diseases.json"), "r") as f:
        diseases_dict = json.load(f)

    required_conditions = []
    for _r in engine.expert.rules:
        if _r["disease"] == disease_id:
            required_conditions = _r["conditions"]
            break
    required_symptom_names = [symptoms_dict.get(code, code) for code in required_conditions]
    matched = bc["proven"]
    matched_names = [symptoms_dict.get(code, code) for code in matched]
    missing = bc["unproven"]
    missing_names = [symptoms_dict.get(code, code) for code in missing]

    disease_info = diseases_dict.get(disease_id, {})
    solution = DETAILED_SOLUTIONS.get(disease_id, {})
    
    return jsonify({
        "is_supported": bc["supported"],
        "disease_name": disease_info.get("name", "?"),
        "required_symptoms": required_symptom_names,
        "matched_symptoms": matched_names,
        "missing_symptoms": missing_names,
        "matched_count": len(matched),
        "total_required": len(required_conditions),
        "recommendation": disease_info.get("recommendation", ""),
        "red_flag": disease_info.get("red_flag", False),
        "first_aid": solution.get("first_aid", []),
        "diet": solution.get("diet", []),
        "medication": solution.get("medication", []),
        "medication_disclaimer": MEDICATION_DISCLAIMER,
        "when_to_hospital": solution.get("when_to_hospital", []),
        "prevention": solution.get("prevention", [])
    })


@app.route('/api/stats')
def api_stats():
    """API endpoint untuk data statistik dashboard"""
    stats = get_dataset_stats()
    stats["model_accuracy"] = getattr(engine.ml, "accuracy", None)
    return jsonify(stats)


# ============================================================
# AI ASSISTANT CHATBOT (Rule-Based)
# ============================================================
def chatbot_reply(message):
    """Membalas pesan user dengan logika berbasis aturan (Bahasa Indonesia)."""
    msg = message.lower().strip()

    with open(os.path.join(data_path, "diseases.json"), "r") as f:
        diseases = json.load(f)
    with open(os.path.join(data_path, "symptoms.json"), "r") as f:
        symptoms = json.load(f)

    # --- Sapaan ---
    if any(w in msg for w in ["halo", "hai", "hello", "hei", "pagi", "siang", "sore", "malam", "assalamu"]):
        return ("Halo! Saya <b>Badrun</b>, asisten medis AI BadrunScreen. "
                "Saya bisa membantu menjelaskan cara memakai aplikasi ini, "
                "memberi info tentang 7 penyakit yang dikenali sistem, atau "
                "menjawab pertanyaan seputar gejala. Ada yang bisa saya bantu?")

    # --- Cara pakai ---
    if any(w in msg for w in ["cara pakai", "cara memakai", "cara menggunakan", "bantuan", "help", "bagaimana cara"]):
        return ("Cara memakai BadrunScreen:<br>"
                "1. Buka bagian <b>Skrining Gejala</b>.<br>"
                "2. Centang semua gejala yang Anda rasakan.<br>"
                "3. Klik <b>Analisis Sekarang</b>.<br>"
                "4. Sistem akan menampilkan kemungkinan penyakit, tingkat keyakinan, "
                "serta solusi lengkap (pertolongan pertama, pola makan, obat, kapan ke RS, pencegahan).")

    # --- Daftar penyakit ---
    if any(w in msg for w in ["daftar penyakit", "penyakit apa saja", "penyakit apa aja", "jenis penyakit"]):
        daftar = "<br>".join([f"• <b>{d['name']}</b>" for d in diseases.values()])
        return f"Saat ini saya mengenali 7 penyakit:<br>{daftar}<br><br>Tanya saya tentang salah satunya, misal: <i>\"apa itu DBD?\"</i>"

    # --- Info per penyakit ---
    disease_keywords = {
        "P01": ["dbd", "demam berdarah", "dengue"],
        "P02": ["influenza", "flu"],
        "P03": ["tifoid", "tipes", "tipus"],
        "P04": ["ispa"],
        "P05": ["diabetes", "gula darah", "kencing manis"],
        "P06": ["covid", "corona"],
        "P07": ["maag", "lambung", "dispepsia", "gerd"],
    }
    for did, keywords in disease_keywords.items():
        if any(k in msg for k in keywords):
            d = diseases[did]
            sol = DETAILED_SOLUTIONS.get(did, {})
            gejala = ", ".join([symptoms.get(g, g) for g in
                                next((r["conditions"] for r in
                                      json.load(open(os.path.join(data_path, "rules.json")))
                                      if r["disease"] == did), [])])
            red = "<br><b>⚠ Tanda bahaya:</b> Penyakit ini punya red flag — segera ke RS jika gejala memburuk." if d.get("red_flag") else ""
            pertolongan = "<br>".join([f"• {x}" for x in sol.get("first_aid", [])[:3]])
            return (f"<b>{d['name']}</b><br><br>"
                    f"<b>Gejala khas:</b> {gejala}.<br><br>"
                    f"<b>Rekomendasi:</b> {d.get('recommendation', '')}{red}<br><br>"
                    f"<b>Pertolongan pertama:</b><br>{pertolongan}<br><br>"
                    f"<i>Untuk analisis personal, gunakan fitur Skrining Gejala ya.</i>")

    # --- Dataset ---
    if "dataset" in msg:
        s = get_dataset_stats()
        return (f"Dataset BadrunScreen berisi <b>{s['total_samples']} kasus</b> pasien simulasi, "
                f"<b>{s['total_features']} gejala</b>, dan <b>{s['total_classes']} penyakit</b> "
                f"(200 kasus per penyakit). Dataset ini dipakai untuk melatih model "
                f"Random Forest di aplikasi ini. Detail lengkap ada di file "
                f"<i>data/DATASET_README.md</i>.")

    # --- Darurat ---
    if any(w in msg for w in ["darurat", "emergency", "gawat", "ambulans", "ambulan"]):
        return ("<b>Kontak darurat Indonesia:</b><br>"
                "• Ambulans / Kegawatdaruratan: <b>118</b> / <b>119</b><br>"
                "• Polisi: <b>110</b><br>"
                "• Pemadam kebakaran: <b>113</b><br><br>"
                "Jika mengalami sesak napas berat, nyeri dada, atau penurunan kesadaran — "
                "segera hubungi 118/119 atau ke IGD terdekat!")

    # --- Terima kasih ---
    if any(w in msg for w in ["terima kasih", "makasih", "thanks", "thank you"]):
        return ("Sama-sama! Senang bisa membantu. Jaga kesehatan ya, "
                "dan ingat: saya hanya alat skrining awal, bukan pengganti dokter.")

    # --- Siapa kamu ---
    if any(w in msg for w in ["siapa kamu", "nama kamu", "namamu"]):
        return ("Saya <b>Badrun</b> — asisten medis AI di BadrunScreen. "
                "Saya membantu menjawab pertanyaan seputar aplikasi, gejala, "
                "dan 7 penyakit yang dikenali sistem.")

    # --- Default ---
    return ("Hmm, saya belum paham pertanyaan itu. Saya bisa bantu soal:<br>"
            "• <i>\"cara pakai\"</i> — panduan aplikasi<br>"
            "• <i>\"daftar penyakit\"</i> — 7 penyakit yang dikenali<br>"
            "• <i>\"apa itu DBD?\"</i> — info penyakit tertentu<br>"
            "• <i>\"kontak darurat\"</i> — nomor penting<br><br>"
            "Atau langsung coba <b>Skrining Gejala</b> untuk analisis.")


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    message = data.get('message', '')
    if not message.strip():
        return jsonify({"reply": "Silakan ketik pesan dulu ya."})
    try:
        reply = chatbot_reply(message)
    except Exception as e:
        reply = "Maaf, terjadi kesalahan. Coba lagi ya."
    return jsonify({"reply": reply})


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, port=5000, use_reloader=False)
