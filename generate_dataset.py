"""
=============================================================================
 GENERATOR DATASET IMITASI - BadrunScreen AI
=============================================================================
 Script ini menghasilkan dataset sintetis/imitasi untuk melatih model
 Machine Learning pada sistem BadrunScreen.

 Dataset dibangun berdasarkan aturan (rules) sistem pakar yang sudah ada,
 dengan variasi realistis:
   - Gejala utama (core symptoms) dari tiap rule penyakit
   - Gejala tambahan yang sering menyertai (associated symptoms)
   - Noise acak untuk mensimulasikan variasi pasien di dunia nyata
   - Variasi jumlah gejala yang muncul (tidak selalu semua gejala muncul)

 Penyakit yang dicakup:
   P01 - Demam Berdarah Dengue (DBD)
   P02 - Influenza
   P03 - Tifoid (Tipes)
   P04 - ISPA
   P05 - Indikasi Diabetes
   P06 - Indikasi COVID-19
   P07 - Gangguan Lambung / Dispepsia (Maag)

 Gejala (G01-G17):
   G01: Demam tinggi            G10: Sering haus (Polidipsia)
   G02: Nyeri sendi/otot        G11: Sering buang air kecil (Poliuria)
   G03: Sakit kepala            G12: Mudah lelah
   G04: Bintik merah di kulit   G13: Diare
   G05: Mual dan muntah         G14: Kehilangan penciuman/perasa (Anosmia)
   G06: Batuk                   G15: Sesak napas
   G07: Pilek / hidung tersumbat G16: Perut kembung / Begah
   G08: Sakit tenggorokan       G17: Sering sendawa
   G09: Nyeri perut
=============================================================================
"""

import csv
import random
import os

# Seed untuk reproducibility
random.seed(42)

# Semua kode gejala
ALL_SYMPTOMS = [f"G{str(i).zfill(2)}" for i in range(1, 18)]

# ============================================================
# PROFIL PENYAKIT
# ============================================================
# Setiap penyakit memiliki:
#   - core_symptoms     : gejala utama (dari rules.json), kemungkinan tinggi muncul
#   - associated        : gejala tambahan yang sering menyertai (realistis secara medis)
#   - core_probability  : probabilitas tiap gejala inti muncul (0.0 - 1.0)
#   - assoc_probability : probabilitas tiap gejala tambahan muncul
#   - noise_probability : probabilitas gejala acak lain muncul (noise)
#   - count             : jumlah sampel yang akan dibuat untuk penyakit ini

DISEASE_PROFILES = {
    "P01": {  # Demam Berdarah Dengue (DBD)
        "core_symptoms":     ["G01", "G02", "G03", "G04"],
        "associated":        ["G05", "G12"],           # Mual dan Mudah lelah sering menyertai DBD
        "core_probability":  0.85,
        "assoc_probability": 0.40,
        "noise_probability": 0.05,
        "count":            200,
    },
    "P02": {  # Influenza
        "core_symptoms":     ["G01", "G06", "G07", "G08"],
        "associated":        ["G02", "G03", "G12"],    # Nyeri sendi, sakit kepala, mudah lelah
        "core_probability":  0.85,
        "assoc_probability": 0.35,
        "noise_probability": 0.05,
        "count":            200,
    },
    "P03": {  # Tifoid (Tipes)
        "core_symptoms":     ["G01", "G05", "G09", "G13"],
        "associated":        ["G03", "G12"],           # Sakit kepala, mudah lelah
        "core_probability":  0.85,
        "assoc_probability": 0.40,
        "noise_probability": 0.05,
        "count":            200,
    },
    "P04": {  # ISPA
        "core_symptoms":     ["G06", "G07", "G08", "G12"],
        "associated":        ["G01", "G03"],           # Demam ringan, sakit kepala
        "core_probability":  0.85,
        "assoc_probability": 0.30,
        "noise_probability": 0.05,
        "count":            200,
    },
    "P05": {  # Indikasi Diabetes
        "core_symptoms":     ["G10", "G11", "G12"],
        "associated":        ["G03", "G05"],           # Sakit kepala, mual
        "core_probability":  0.90,
        "assoc_probability": 0.25,
        "noise_probability": 0.04,
        "count":            200,
    },
    "P06": {  # Indikasi COVID-19
        "core_symptoms":     ["G01", "G06", "G12", "G14", "G15"],
        "associated":        ["G02", "G03", "G08"],    # Nyeri sendi, sakit kepala, sakit tenggorokan
        "core_probability":  0.82,
        "assoc_probability": 0.35,
        "noise_probability": 0.05,
        "count":            200,
    },
    "P07": {  # Gangguan Lambung / Dispepsia (Maag)
        "core_symptoms":     ["G05", "G09", "G16", "G17"],
        "associated":        ["G03", "G12"],           # Sakit kepala, mudah lelah
        "core_probability":  0.85,
        "assoc_probability": 0.30,
        "noise_probability": 0.04,
        "count":            200,
    },
}


def generate_sample(profile, disease_id):
    """
    Menghasilkan satu baris sampel data berdasarkan profil penyakit.
    Mengembalikan dict {G01: 0/1, G02: 0/1, ..., G17: 0/1, Target: disease_id}
    """
    row = {g: 0 for g in ALL_SYMPTOMS}

    core = profile["core_symptoms"]
    assoc = profile["associated"]
    other = [g for g in ALL_SYMPTOMS if g not in core and g not in assoc]

    # Pastikan minimal 2 gejala inti muncul (agar data masih bermakna)
    # Pertama, tentukan semua gejala inti berdasarkan probabilitas
    core_activated = []
    for g in core:
        if random.random() < profile["core_probability"]:
            row[g] = 1
            core_activated.append(g)

    # Jika kurang dari 2 gejala inti, paksa tambahkan
    while len(core_activated) < min(2, len(core)):
        remaining = [g for g in core if g not in core_activated]
        if not remaining:
            break
        chosen = random.choice(remaining)
        row[chosen] = 1
        core_activated.append(chosen)

    # Gejala tambahan (associated)
    for g in assoc:
        if random.random() < profile["assoc_probability"]:
            row[g] = 1

    # Noise: gejala acak lain (simulasi ketidakteraturan data dunia nyata)
    for g in other:
        if random.random() < profile["noise_probability"]:
            row[g] = 1

    row["Target"] = disease_id
    return row


def generate_dataset():
    """
    Menghasilkan seluruh dataset dan menyimpannya sebagai CSV.
    """
    dataset = []

    for disease_id, profile in DISEASE_PROFILES.items():
        for _ in range(profile["count"]):
            sample = generate_sample(profile, disease_id)
            dataset.append(sample)

    # Acak urutan data agar tidak berurutan per penyakit
    random.shuffle(dataset)

    return dataset


def save_csv(dataset, filepath):
    """
    Menyimpan dataset ke file CSV.
    """
    fieldnames = ALL_SYMPTOMS + ["Target"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)


def print_summary(dataset):
    """
    Menampilkan ringkasan statistik dataset.
    """
    from collections import Counter

    target_counts = Counter(row["Target"] for row in dataset)

    disease_names = {
        "P01": "Demam Berdarah Dengue (DBD)",
        "P02": "Influenza",
        "P03": "Tifoid (Tipes)",
        "P04": "ISPA",
        "P05": "Indikasi Diabetes",
        "P06": "Indikasi COVID-19",
        "P07": "Gangguan Lambung / Dispepsia (Maag)",
    }

    print("=" * 60)
    print("   RINGKASAN DATASET IMITASI - BadrunScreen AI")
    print("=" * 60)
    print(f"   Total Sampel       : {len(dataset)}")
    print(f"   Jumlah Fitur       : {len(ALL_SYMPTOMS)} gejala (G01-G17)")
    print(f"   Jumlah Kelas       : {len(target_counts)} penyakit")
    print("-" * 60)
    print(f"   {'Kode':<6} {'Penyakit':<42} {'Jumlah':>6}")
    print("-" * 60)
    for disease_id in sorted(target_counts.keys()):
        name = disease_names.get(disease_id, "?")
        count = target_counts[disease_id]
        print(f"   {disease_id:<6} {name:<42} {count:>6}")
    print("-" * 60)

    # Hitung rata-rata gejala per sampel
    avg_symptoms = sum(
        sum(row[g] for g in ALL_SYMPTOMS) for row in dataset
    ) / len(dataset)
    print(f"   Rata-rata gejala per pasien: {avg_symptoms:.1f}")
    print("=" * 60)


if __name__ == "__main__":
    # Path output
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "data", "dataset.csv")

    # Generate & simpan
    dataset = generate_dataset()
    save_csv(dataset, output_path)
    print_summary(dataset)
    print(f"\n   Dataset berhasil disimpan ke:\n   {output_path}\n")
