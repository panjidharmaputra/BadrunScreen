"""
Expert System BadrunScreen — Mesin Inferensi Forward Chaining & Backward Chaining.

Basis pengetahuan: data/rules.json berisi aturan produksi berbentuk
    IF (G01 AND G02 AND G03 AND G04) THEN (Penyakit P0x)

Dua arah penalaran diimplementasikan secara terpisah agar bisa
dijelaskan/didemokan satu per satu (kebutuhan mata kuliah Kecerdasan Buatan):

1. FORWARD CHAINING (data-driven / bottom-up)
   - Fakta awal (working memory) = gejala yang dicentang user.
   - Setiap aturan dievaluasi: bila SEMUA kondisinya ada di working memory,
     aturan MENYALA (fired) dan kesimpulannya (penyakit) masuk ke working memory.
   - Aturan yang hanya cocok sebagian tetap dicatat sebagai kandidat dengan
     skor rule-coverage, beserta trace langkah inferensinya.

2. BACKWARD CHAINING (goal-driven / top-down)
   - Dimulai dari HIPOTESIS (satu penyakit kandidat).
   - Hipotesis dipecah menjadi sub-goal (kondisi-kondisinya), lalu setiap
     sub-goal diverifikasi terhadap fakta yang diketahui (gejala user).
     Bila sebuah kondisi adalah fakta turunan (penyakit lain), verifikasi
     dilakukan secara rekursif.
   - Menghasilkan skor dukungan (support) + pohon pembuktian (proof trace).
"""

import json
import os


class ExpertSystem:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.rules = self._load_json("rules.json")
        self.diseases = self._load_json("diseases.json")
        self.symptoms = self._load_json("symptoms.json")

    # ------------------------------------------------------------------ util
    def _load_json(self, filename):
        path = os.path.join(self.data_path, filename)
        with open(path, "r") as f:
            return json.load(f)

    def _symptom_name(self, code):
        return self.symptoms.get(code, code)

    def _disease_name(self, disease_id):
        return self.diseases.get(disease_id, {}).get("name", disease_id)

    # ================================================================
    # FORWARD CHAINING
    # ================================================================
    def forward_chaining(self, user_symptoms):
        """
        Penalaran maju: dari FAKTA (gejala user) menuju KESIMPULAN (penyakit).

        Langkah:
          1. Working memory diisi fakta awal = gejala user.
          2. Setiap aturan dievaluasi berurutan:
             - semua kondisi terpenuhi  -> aturan MENYALA, penyakit masuk WM.
             - sebagian terpenuhi       -> kandidat parsial (skor coverage).
          3. Trace mencatat urutan evaluasi tiap aturan.

        Returns:
            (candidates, trace, fired_rules)
            candidates : list kandidat terurut (confidence tertinggi dulu)
            trace      : list langkah inferensi (dict, siap dirender UI)
            fired_rules: aturan yang menyala penuh
        """
        wm = set(user_symptoms)          # working memory = fakta yang diketahui
        trace = []
        fired_rules = []
        candidates = []

        for rule in self.rules:
            rule_id = rule.get("id", "?")
            disease_id = rule["disease"]
            conditions = rule["conditions"]

            matched = [c for c in conditions if c in wm]
            missing = [c for c in conditions if c not in wm]
            fired = len(missing) == 0

            step = {
                "rule_id": rule_id,
                "disease_id": disease_id,
                "disease_name": self._disease_name(disease_id),
                "conditions": conditions,
                "condition_names": [self._symptom_name(c) for c in conditions],
                "matched": matched,
                "matched_names": [self._symptom_name(c) for c in matched],
                "missing": missing,
                "missing_names": [self._symptom_name(c) for c in missing],
                "fired": fired,
            }
            trace.append(step)

            if fired:
                # Kesimpulan aturan menjadi fakta baru di working memory
                wm.add(disease_id)
                fired_rules.append(step)

            if matched:
                confidence = (len(matched) / len(conditions)) * 100
                candidates.append({
                    "disease_id": disease_id,
                    "disease_name": self._disease_name(disease_id),
                    "forward_confidence": round(confidence, 2),
                    "matched_symptoms": matched,
                    "missing_symptoms": missing,
                    "fired": fired,
                })

        candidates.sort(key=lambda x: x["forward_confidence"], reverse=True)
        return candidates, trace, fired_rules

    # ================================================================
    # BACKWARD CHAINING
    # ================================================================
    def backward_chaining(self, hypothesis_disease_id, user_symptoms, _depth=0, _visited=None):
        """
        Penalaran mundur: dari HIPOTESIS (penyakit) menuju FAKTA pendukung.

        Langkah:
          1. Ambil aturan untuk hipotesis penyakit tersebut.
          2. Setiap kondisi dijadikan sub-goal dan diverifikasi:
             - ada di gejala user            -> TERBUKTI (fakta)
             - adalah penyakit lain (turunan) -> diverifikasi REKURSIF
             - tidak ada                      -> GAGAL dibuktikan
          3. Skor dukungan = kondisi terbukti / total kondisi.

        Returns:
            {
              "disease_id", "disease_name",
              "supported"      : bool (True bila semua kondisi terbukti),
              "support_score"  : float 0-100,
              "proof"          : list langkah pembuktian (dengan depth utk indentasi),
              "proven"         : kondisi yang terbukti,
              "unproven"       : kondisi yang gagal dibuktikan,
            }
        """
        if _visited is None:
            _visited = set()
        facts = set(user_symptoms)
        proof = []
        proven = []
        unproven = []

        # Cari aturan untuk hipotesis ini
        target_rules = [r for r in self.rules if r["disease"] == hypothesis_disease_id]
        if not target_rules:
            return {
                "disease_id": hypothesis_disease_id,
                "disease_name": self._disease_name(hypothesis_disease_id),
                "supported": False,
                "support_score": 0.0,
                "proof": [{"depth": _depth, "text": "Tidak ada aturan untuk hipotesis ini.", "status": "fail"}],
                "proven": [],
                "unproven": [],
            }

        for rule in target_rules:
            rule_id = rule.get("id", "?")
            proof.append({
                "depth": _depth,
                "text": "Hipotesis: {} — uji aturan {} (butuh: {})".format(
                    self._disease_name(hypothesis_disease_id),
                    rule_id,
                    ", ".join(self._symptom_name(c) for c in rule["conditions"]),
                ),
                "status": "goal",
            })
            for cond in rule["conditions"]:
                if cond in facts:
                    proven.append(cond)
                    proof.append({
                        "depth": _depth + 1,
                        "text": "Sub-goal {} ({}) — TERBUKTI dari gejala user".format(
                            cond, self._symptom_name(cond)),
                        "status": "ok",
                    })
                elif cond in self.diseases and cond not in _visited:
                    # Fakta turunan: verifikasi hipotesis perantara secara rekursif
                    _visited.add(cond)
                    proof.append({
                        "depth": _depth + 1,
                        "text": "Sub-goal {} ({}) — fakta turunan, verifikasi rekursif...".format(
                            cond, self._disease_name(cond)),
                        "status": "recurse",
                    })
                    sub = self.backward_chaining(cond, user_symptoms, _depth + 2, _visited)
                    proof.extend(sub["proof"])
                    if sub["supported"]:
                        proven.append(cond)
                    else:
                        unproven.append(cond)
                else:
                    unproven.append(cond)
                    proof.append({
                        "depth": _depth + 1,
                        "text": "Sub-goal {} ({}) — TIDAK terbukti (tidak ada di gejala user)".format(
                            cond, self._symptom_name(cond)),
                        "status": "fail",
                    })

        total = len(proven) + len(unproven)
        support_score = (len(proven) / total * 100) if total else 0.0
        proof.append({
            "depth": _depth,
            "text": "Kesimpulan: hipotesis {} {} (dukungan {}/{}, {:.1f}%)".format(
                self._disease_name(hypothesis_disease_id),
                "TERBUKTI PENUH" if not unproven else "terdukung sebagian",
                len(proven), total, support_score,
            ),
            "status": "ok" if not unproven else "partial",
        })

        return {
            "disease_id": hypothesis_disease_id,
            "disease_name": self._disease_name(hypothesis_disease_id),
            "supported": len(unproven) == 0,
            "support_score": round(support_score, 2),
            "proof": proof,
            "proven": proven,
            "unproven": unproven,
        }

    # ================================================================
    # KOMBINASI: forward (kandidat) + backward (verifikasi)
    # ================================================================
    def diagnose(self, user_symptoms):
        """
        Alur diagnosis lengkap expert system:
          1. Forward chaining  -> daftar kandidat penyakit.
          2. Backward chaining -> tiap kandidat diverifikasi sebagai hipotesis.
          3. Skor expert = 70% forward coverage + 30% backward support.

        Returns: (results, forward_trace, backward_proofs)
        """
        candidates, forward_trace, _fired = self.forward_chaining(user_symptoms)

        results = []
        backward_proofs = {}
        for cand in candidates:
            bc = self.backward_chaining(cand["disease_id"], user_symptoms)
            backward_proofs[cand["disease_id"]] = bc["proof"]

            expert_confidence = round(
                cand["forward_confidence"] * 0.7 + bc["support_score"] * 0.3, 2
            )
            results.append({
                **cand,
                "backward_confidence": bc["support_score"],
                "backward_verified": bc["supported"],
                "expert_confidence": expert_confidence,
            })

        results.sort(key=lambda x: x["expert_confidence"], reverse=True)
        return results, forward_trace, backward_proofs
