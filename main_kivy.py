import os
import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from engine.hybrid_engine import HybridEngine
from kivy.core.window import Window

# Atur ukuran jendela mirip layar HP untuk ujicoba di laptop
Window.size = (360, 640)

KV = '''
MDScreenManager:
    InputScreen:
    ResultScreen:

<SymptomListItem>
    text: root.text
    secondary_text: root.secondary_text

<InputScreen>:
    name: "input"
    
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "BadrunScreen AI"
            elevation: 4
            left_action_items: [["hospital-box"]]
            
        MDLabel:
            text: "Pilih gejala yang Anda rasakan:"
            halign: "center"
            size_hint_y: None
            height: "40dp"
            font_style: "Subtitle2"
            
        ScrollView:
            MDList:
                id: symptoms_list
                
        MDFillRoundFlatButton:
            text: "PROSES ANALISIS"
            pos_hint: {"center_x": .5}
            size_hint_x: 0.8
            on_release: app.process_analysis()
            
        Widget:
            size_hint_y: None
            height: "20dp"

<ResultScreen>:
    name: "result"
    
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Hasil Skrining"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            elevation: 4
            
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"
                adaptive_height: True
                
                MDLabel:
                    id: result_title
                    text: "Indikasi Penyakit:"
                    font_style: "H6"
                    adaptive_height: True
                    theme_text_color: "Primary"
                    
                MDLabel:
                    id: confidence_label
                    text: "Keyakinan:"
                    font_style: "Subtitle1"
                    theme_text_color: "Secondary"
                    adaptive_height: True
                    
                MDSeparator:
                
                MDLabel:
                    text: "Rekomendasi Tindakan:"
                    font_style: "Subtitle2"
                    adaptive_height: True
                    bold: True
                    
                MDLabel:
                    id: recommendation_label
                    text: ""
                    adaptive_height: True
                    
                MDSeparator:
                
                MDLabel:
                    id: warning_label
                    text: ""
                    theme_text_color: "Error"
                    font_style: "Subtitle2"
                    adaptive_height: True
'''

class SymptomListItem(TwoLineAvatarIconListItem):
    pass

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass

class InputScreen(MDScreen):
    pass

class ResultScreen(MDScreen):
    pass

class SymptoApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        # Load Hybrid Engine AI
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data")
        self.engine = HybridEngine(data_path)
        
        # Load Knowledge Base Data
        with open(os.path.join(data_path, "symptoms.json"), "r") as f:
            self.symptoms = json.load(f)
            
        with open(os.path.join(data_path, "diseases.json"), "r") as f:
            self.diseases = json.load(f)
            
        return Builder.load_string(KV)

    def on_start(self):
        # Memasukkan daftar gejala ke layar list
        screen = self.root.get_screen('input')
        self.checkboxes = {}
        for code, name in self.symptoms.items():
            item = SymptomListItem(text=name, secondary_text=code)
            checkbox = RightCheckbox()
            self.checkboxes[code] = checkbox
            item.add_widget(checkbox)
            screen.ids.symptoms_list.add_widget(item)

    def process_analysis(self):
        # Mengambil gejala yang dicentang oleh user
        selected_symptoms = [code for code, cb in self.checkboxes.items() if cb.active]
        if not selected_symptoms:
            return # User tidak memilih gejala, batal proses
            
        # Panggil AI Engine
        results = self.engine.process_screening(selected_symptoms)
        
        # Tampilkan Hasil
        result_screen = self.root.get_screen('result')
        if results:
            top_result = results[0]
            disease_info = self.diseases[top_result["disease_id"]]
            
            result_screen.ids.result_title.text = f"Penyakit: {disease_info['name']}"
            result_screen.ids.confidence_label.text = f"Tingkat Keyakinan AI: {top_result['hybrid_confidence']}%"
            result_screen.ids.recommendation_label.text = disease_info["recommendation"]
            
            if disease_info["red_flag"]:
                result_screen.ids.warning_label.text = "⚠ PERINGATAN (RED FLAG) ⚠\\nJika kondisi memburuk, segera temui dokter atau ke IGD!"
            else:
                result_screen.ids.warning_label.text = "Hasil skrining bukan diagnosis medis. Konsultasikan dengan dokter untuk kepastian."
        else:
            result_screen.ids.result_title.text = "Pola Gejala Tidak Dikenali"
            result_screen.ids.confidence_label.text = ""
            result_screen.ids.recommendation_label.text = "Kami belum bisa menemukan kecocokan dalam sistem kami."
            result_screen.ids.warning_label.text = ""
            
        # Pindah ke layar hasil
        self.root.current = 'result'

    def go_back(self):
        self.root.current = 'input'

if __name__ == '__main__':
    SymptoApp().run()
