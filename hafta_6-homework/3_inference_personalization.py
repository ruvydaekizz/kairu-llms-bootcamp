"""
Inference ve Kişiselleştirilmiş Model Kullanımı (movie_metadata.csv + fine_tuned_model)

Özellikler:
- ./fine_tuned_model içindeki modeli yükler
- Tek örnek / batch örnek sınıflandırma
- Eval dataset üzerinde confusion matrix ve classification report
- label isimleri model.config.id2label'dan otomatik okunur
"""

import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset
from sklearn.metrics import confusion_matrix, classification_report
from collections import Counter

MODEL_DIR = "./fine_tuned_model"
DATA_PATH = "data/movie_metadata.csv"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class PersonalizedInference:
    def __init__(self, model_path=MODEL_DIR, device=DEVICE):
        self.model_path = model_path
        self.device = device
        self._load()

    def _load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        try:
            id2label = self.model.config.id2label
            max_key = max(int(k) for k in id2label.keys())
            self.label_names = [id2label.get(str(i), id2label.get(i, f"LABEL_{i}")) for i in range(max_key+1)]
        except Exception:
            self.label_names = ["NEGATIVE", "POSITIVE"]

    def classify_text(self, texts, max_length=512):
        single = False
        if isinstance(texts, str):
            texts = [texts]
            single = True

        enc = self.tokenizer(texts, truncation=True, padding=True, max_length=max_length, return_tensors="pt")
        enc = {k: v.to(self.device) for k, v in enc.items()}

        with torch.no_grad():
            outputs = self.model(**enc)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()

        results = []
        for p in probs:
            pred_idx = int(np.argmax(p))
            results.append({
                "predicted_class": pred_idx,
                "predicted_label": self.label_names[pred_idx] if pred_idx < len(self.label_names) else str(pred_idx),
                "probabilities": p.tolist(),
                "confidence": float(p[pred_idx])
            })
        return results[0] if single else results

    def evaluate_on_csv(self, csv_path=DATA_PATH, batch_size=32):
        ds = load_dataset("csv", data_files={"full": csv_path})["full"]
        texts, y_true = [], []
        for ex in ds:
            try:
                rating = float(ex["imdb_score"])
            except Exception:
                continue
            texts.append(ex["movie_title"])
            y_true.append(1 if rating > 7.0 else 0)

        preds = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_results = self.classify_text(batch)
            preds.extend([r["predicted_class"] for r in batch_results])

        y_true_arr = np.array(y_true)
        preds_arr = np.array(preds)

        print("Confusion matrix:")
        try:
            cm = confusion_matrix(y_true_arr, preds_arr, labels=[0,1])
            print(cm)
        except Exception as e:
            print("Confusion matrix oluşturulamadı:", e)
            print("y_true dağılım:", Counter(y_true_arr.tolist()))
            print("preds dağılım:", Counter(preds_arr.tolist()))

        print("\nClassification report:")
        try:
            print(classification_report(y_true_arr, preds_arr, target_names=self.label_names, zero_division=0))
        except Exception as e:
            print("classification_report oluşturulamadı:", e)

        return y_true_arr, preds_arr

    def personalize_prompt(self, user_profile, user_input):
        prompt = f"""Kullanıcı Profili:
- İsim: {user_profile.get('name')}
- İlgi Alanları: {', '.join(user_profile.get('interests', []))}
- Stil: {user_profile.get('style')}

Soru: {user_input}
"""
        return prompt

if __name__ == "__main__":
    engine = PersonalizedInference(model_path=MODEL_DIR)

    # Tek örnek
    sample = "Bu film gerçekten müthişti, oyunculuk harikaydı."
    print("Tek örnek sonucu:")
    print(engine.classify_text(sample))

    # Batch örnekler
    batch_samples = [
        "Berbat bir filmdi, zaman kaybı.",
        "Güzel anlatılmış, duygusal bir yapım.",
        "Efektler çok etkileyiciydi ama hikaye zayıftı."
    ]
    print("\nBatch sonuçları:")
    for txt, res in zip(batch_samples, engine.classify_text(batch_samples)):
        print(f"Text: {txt}\n => {res}\n")

    # Eval dataset üzerinde rapor
    print("\n=== Eval dataset üzerinde model performansı (CSV tabanlı) ===")
    y_true, y_pred = engine.evaluate_on_csv()

    # Kişiselleştirme örneği
    user_profile = {
        "name": "Ayşe",
        "interests": ["sinema", "hikaye", "müzik"],
        "style": "samimi ve kısa öneriler"
    }
    print("\nPersonalized prompt (örnek):")
    print(engine.personalize_prompt(user_profile, "Bana ailece izleyebileceğimiz bir film önerir misin?"))
