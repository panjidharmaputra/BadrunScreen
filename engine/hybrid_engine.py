from .expert_system import ExpertSystem
from .ml_engine import MLEngine
import os

class HybridEngine:
    """
    Hybrid AI BadrunScreen:
      Expert System (Forward + Backward Chaining)  -> bobot 60%
      Machine Learning (Random Forest)             -> bobot 40%
    """
    def __init__(self, data_path="data"):
        self.expert = ExpertSystem(data_path)
        self.ml = MLEngine(data_path)
        self.ml.train()  # Latih model saat inisialisasi

    def process_screening(self, user_symptoms):
        """
        Alur hybrid:
          1. Expert System:
             - Forward chaining  -> kandidat penyakit dari fakta gejala.
             - Backward chaining -> tiap kandidat diverifikasi sebagai hipotesis.
             - Skor expert = 70% forward coverage + 30% backward support.
          2. Machine Learning (Random Forest) -> prediksi probabilitas.
          3. Hybrid decision:
             - bila ML menunjuk penyakit yang sama -> 60% expert + 40% ML.
             - bila tidak -> skor expert apa adanya.

        Returns: (final_diagnosis, forward_trace, backward_proofs)
        """
        # 1. Expert system: forward + backward chaining
        expert_results, forward_trace, backward_proofs = self.expert.diagnose(user_symptoms)

        # 2. Machine Learning
        ml_result = self.ml.predict(user_symptoms)

        # 3. Hybrid decision (voting tertimbang)
        final_diagnosis = []
        for er in expert_results:
            disease_id = er["disease_id"]
            expert_conf = er["expert_confidence"]

            if ml_result and ml_result["disease_id"] == disease_id:
                combined = (expert_conf * 0.6) + (ml_result["probability"] * 0.4)
                er["hybrid_confidence"] = round(combined, 2)
                er["ml_supported"] = True
                er["ml_probability"] = round(ml_result["probability"], 2)
            else:
                er["hybrid_confidence"] = round(expert_conf, 2)
                er["ml_supported"] = False
                er["ml_probability"] = None

            final_diagnosis.append(er)

        final_diagnosis.sort(key=lambda x: x["hybrid_confidence"], reverse=True)
        return final_diagnosis, forward_trace, backward_proofs
