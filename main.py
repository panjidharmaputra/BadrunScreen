import os
import json
from engine.hybrid_engine import HybridEngine

def print_header():
    print("="*50)
    print(" "*10 + "BADRUNSCREEN AI - CLI (MVP)")
    print("="*50)
    print("Peringatan: Aplikasi ini HANYA ALAT SKRINING AWAL.")
    print("Bukan diagnosis pasti dan tidak menggantikan dokter.")
    print("="*50)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data")
    
    # Init Hybrid Engine
    engine = HybridEngine(data_path)
    
    # Load symptoms for display
    with open(os.path.join(data_path, "symptoms.json"), "r") as f:
        symptoms_dict = json.load(f)
        
    with open(os.path.join(data_path, "diseases.json"), "r") as f:
        diseases_dict = json.load(f)
        
    print_header()
    print("Daftar Gejala:")
    for code, name in symptoms_dict.items():
        print(f"[{code}] {name}")
        
    print("\nMasukkan kode gejala yang Anda rasakan (pisahkan dengan koma).")
    print("Contoh: G01, G02, G06")
    user_input = input("Gejala Anda: ").strip().upper()
    
    if not user_input:
        print("Anda tidak memasukkan gejala.")
        return
        
    user_symptoms = [s.strip() for s in user_input.split(",")]
    
    print("\n[Memproses Data...]")
    results = engine.process_screening(user_symptoms)
    
    if not results:
        print("Sistem tidak menemukan pola penyakit yang cocok.")
    else:
        print("\n--- HASIL SKRINING ---")
        top_result = results[0]
        disease_info = diseases_dict[top_result["disease_id"]]
        
        print(f"Berdasarkan analisis, indikasi penyakit utama: {disease_info['name']}")
        print(f"Tingkat Keyakinan Sistem (Hybrid Confidence): {top_result['hybrid_confidence']}%")
        print(f"Didukung oleh Machine Learning: {'Ya' if top_result['ml_supported'] else 'Tidak'}")
        
        print(f"\nAlasan Sistem Pakar (Rule-Based):")
        print(f"- Gejala Anda yang cocok: {top_result['matched_symptoms']}")
        if top_result['missing_symptoms']:
            print(f"- Gejala lain yang biasanya ada: {top_result['missing_symptoms']}")
            
        print(f"\nRekomendasi Tindakan:")
        print(disease_info["recommendation"])
        
        if disease_info["red_flag"]:
            print("\n[!!! RED FLAG !!!]")
            print("Penyakit ini berpotensi bahaya! Jika gejala memburuk, SEGERA cari pertolongan medis.")
            
    print("\nTerima kasih telah menggunakan BadrunScreen.")

if __name__ == "__main__":
    main()
