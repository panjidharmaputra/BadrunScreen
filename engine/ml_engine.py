import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

class MLEngine:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.features = []
        self.is_trained = False
        self.accuracy = None

    def train(self):
        """
        Melatih model berdasarkan data di dataset.csv
        """
        path = os.path.join(self.data_path, "dataset.csv")
        if not os.path.exists(path):
            print("Dataset tidak ditemukan. Batal melatih model.")
            return False

        df = pd.read_csv(path)

        # Memisahkan Fitur (Gejala) dan Target (Penyakit)
        X = df.drop("Target", axis=1)
        y = df["Target"]

        self.features = X.columns.tolist()

        # Evaluasi akurasi dengan split 80/20 (untuk ditampilkan di dashboard)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        eval_model = RandomForestClassifier(n_estimators=50, random_state=42)
        eval_model.fit(X_train, y_train)
        self.accuracy = round(accuracy_score(y_test, eval_model.predict(X_test)) * 100, 1)

        # Training Model final dengan seluruh data
        self.model.fit(X, y)
        self.is_trained = True
        return True

    def predict(self, user_symptoms):
        """
        Memprediksi penyakit dan probabilitasnya berdasarkan input gejala
        """
        if not self.is_trained:
            return None
            
        # Membuat vektor input: 1 jika gejala ada, 0 jika tidak
        input_vector = [1 if feature in user_symptoms else 0 for feature in self.features]
        
        # Prediksi kelas
        pred_class = self.model.predict([input_vector])[0]
        
        # Prediksi probabilitas (hanya kelas yang terpilih)
        probs = self.model.predict_proba([input_vector])[0]
        max_prob = max(probs) * 100
        
        return {
            "disease_id": pred_class,
            "probability": max_prob
        }
