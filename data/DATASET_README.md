# Dokumentasi Dataset — BadrunScreen AI

## Ringkasan
| Atribut | Nilai |
|---|---|
| Nama file | `dataset.csv` |
| Jumlah sampel (baris data) | **1400** |
| Jumlah fitur | **17** (gejala G01–G17, biner 0/1) |
| Jumlah kelas (target) | **7** penyakit (P01–P07) |
| Distribusi kelas | Seimbang — 200 sampel per penyakit |
| Rata-rata gejala per pasien | ± 4,7 gejala |
| Format | CSV, header: `G01,...,G17,Target` |

## Jenis Dataset
**Dataset imitasi/sintetis** — dibuat khusus untuk kebutuhan akademik
(tugas proyek Kecerdasan Buatan). Dataset ini **bukan data pasien sungguhan**,
melainkan disimulasikan berdasarkan aturan sistem pakar (`rules.json`) yang
disusun dari pengetahuan umum gejala penyakit.

Dibuat dengan: `python3 generate_dataset.py` (seed `42` → hasil reproducible).

## Cara Dataset Dibuat (`generate_dataset.py`)
Setiap penyakit punya **profil probabilistik**:
- **Gejala inti** (`core_symptoms`, dari `rules.json`): muncul dengan
  probabilitas ± 0,82–0,90 per gejala; minimal 2 gejala inti selalu aktif
  agar tiap sampel tetap bermakna.
- **Gejala penyerta** (`associated`, realistis secara medis, mis. mual
  menyertai DBD): probabilitas ± 0,25–0,40.
- **Noise** (`noise_probability` ± 0,04–0,05): gejala acak lain untuk
  mensimulasikan variasi pasien di dunia nyata.

Urutan baris diacak (`random.shuffle`) agar tidak berurutan per penyakit.

## Kamus Data (Data Dictionary)

### Fitur (kolom G01–G17) — nilai 1 = gejala dialami, 0 = tidak
| Kode | Nama Gejala | Kode | Nama Gejala |
|---|---|---|---|
| G01 | Demam tinggi | G10 | Sering haus (Polidipsia) |
| G02 | Nyeri sendi/otot | G11 | Sering buang air kecil (Poliuria) |
| G03 | Sakit kepala | G12 | Mudah lelah |
| G04 | Bintik merah di kulit | G13 | Diare |
| G05 | Mual dan muntah | G14 | Kehilangan penciuman/perasa (Anosmia) |
| G06 | Batuk | G15 | Sesak napas |
| G07 | Pilek / hidung tersumbat | G16 | Perut kembung / Begah |
| G08 | Sakit tenggorokan | G17 | Sering sendawa |
| G09 | Nyeri perut | | |

### Target (kolom `Target`)
| Kode | Penyakit |
|---|---|
| P01 | Demam Berdarah Dengue (DBD) |
| P02 | Influenza |
| P03 | Tifoid (Tipes) |
| P04 | ISPA (Infeksi Saluran Pernapasan Akut) |
| P05 | Indikasi Diabetes |
| P06 | Indikasi COVID-19 |
| P07 | Gangguan Lambung / Dispepsia (Maag) |

## Penggunaan dalam Program
1. **Pelatihan model ML** — `engine/ml_engine.py` melatih
   `RandomForestClassifier` (50 trees) dengan 17 fitur gejala sebagai `X`
   dan kode penyakit sebagai `y` setiap aplikasi dijalankan.
2. **Hybrid Engine** — `engine/hybrid_engine.py` menggabungkan hasil
   sistem pakar (forward chaining, bobot 60%) dengan prediksi ML
   (bobot 40%) menjadi *hybrid confidence*.
3. **Dashboard statistik** — aplikasi web membaca `dataset.csv` untuk
   menampilkan total kasus, distribusi kelas, dan frekuensi gejala
   secara visual (diagram batang & donat).

## Keterbatasan (Disclaimer Akademik)
- Data bersifat **simulasi**, bukan rekam medis asli.
- Tidak boleh dipakai untuk diagnosis klinis sesungguhnya.
- Aplikasi BadrunScreen adalah **alat skrining awal / media pembelajaran**,
  bukan pengganti dokter.

## Cara Regenerasi
```bash
cd BadrunScreen
python3 generate_dataset.py
```
Ubah `count` pada `DISEASE_PROFILES` di `generate_dataset.py`
untuk mengatur jumlah sampel per penyakit.
