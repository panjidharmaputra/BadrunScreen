# BadrunScreen AI 🩺🤖

Sistem skrining kesehatan cerdas berbasis **Hybrid AI** — menggabungkan
**Sistem Pakar** (forward & backward chaining) dengan **Machine Learning**
(Random Forest) untuk menganalisis gejala dan memberikan solusi penanganan lengkap.

Dibuat untuk **Proyek Kecerdasan Buatan** — Universitas Pamulang.

## Fitur
- 🔍 **Skrining Gejala Interaktif** — 17 gejala dalam 4 kategori, hasil berurutan + solusi lengkap
- 📊 **Dashboard Statistik** — 1.400 kasus dataset, distribusi penyakit, grafik gejala, akurasi model
- 📚 **Ensiklopedia 7 Penyakit** — detail gejala, pertolongan pertama, pola makan, obat, kapan ke RS, pencegahan
- 🤖 **Badrun, Asisten AI** — chatbot pendamping (klik ikon karakter di kanan bawah)
- 🧰 **Tools**: Kalkulator BMI, Mitos vs Fakta kesehatan, Riwayat skrining, Kontak darurat
- 🗂️ **Dataset imitasi** (1.400 sampel) + dokumentasi lengkap di `data/DATASET_README.md`

## Cara Menjalankan (Web)
```bash
cd BadrunScreen
pip install flask pandas scikit-learn
python main_web.py
```
Buka http://127.0.0.1:5000 — browser terbuka otomatis.

## Cara Menjalankan (CLI)
```bash
python main.py
```

## Struktur
```
BadrunScreen/
├── main_web.py          # Aplikasi web Flask + solusi detail + chatbot Badrun
├── main.py              # Versi CLI
├── main_kivy.py         # Versi Kivy (mobile/desktop GUI)
├── generate_dataset.py  # Generator dataset imitasi (1.400 sampel)
├── engine/
│   ├── expert_system.py # Forward & backward chaining
│   ├── ml_engine.py     # Random Forest + evaluasi akurasi
│   └── hybrid_engine.py # Penggabung 60% pakar + 40% ML
├── data/
│   ├── dataset.csv      # Dataset (17 fitur gejala + target penyakit)
│   ├── DATASET_README.md# Dokumentasi dataset
│   ├── symptoms.json    # 17 gejala
│   ├── diseases.json    # 7 penyakit
│   └── rules.json       # Aturan sistem pakar
├── templates/index.html # UI BadrunScreen (dashboard + chatbot + tools)
└── static/img/          # Logo, karakter AI Badrun
```

## Catatan
- Dataset bersifat **simulasi untuk kebutuhan akademik**, bukan data pasien asli.
- Aplikasi ini **alat skrining awal**, bukan diagnosis medis dan tidak menggantikan dokter.
