import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chatbot sınıfı
class EduChatbot:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": "Sen eğitim ve dil öğrenimi için bir asistansın. "
                        "Kullanıcıya yabancı dil öğrenmede yardımcı oluyorsun. "
                        "Bilinmeyen kelimeleri kelime notlarına kaydediyorsun. "
                        "Ayrıca genel notları da tutabiliyorsun."
            }
        ]
        self.user_data = {
            "notes": [],  # <-- Genel Notlar
            "words": []   # <-- Kelime Notları
        }

    def save_note(self, note_text):
        """Genel not kaydetme"""
        note = {
            "id": len(self.user_data["notes"]) + 1,
            "text": note_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.user_data["notes"].append(note)
        return {"message": "Not kaydedildi", "note_id": note["id"]}

    def save_word(self, word, meaning=None):
        """Kelime notu kaydetme"""
        entry = {
            "id": len(self.user_data["words"]) + 1,
            "word": word,
            "meaning": meaning if meaning else "Henüz açıklama yok",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.user_data["words"].append(entry)
        return {"message": "Kelime kaydedildi", "word_id": entry["id"]}

    def list_notes(self):
        return self.user_data["notes"]

    def list_words(self):
        return self.user_data["words"]

    def chat(self, user_message):
        """Chat yanıtı ve komut işlemleri"""

        # Komut İşleme Blokları (Komutlar burada öncelikli olarak kontrol edilir)
        
        # 🔹 Kelime kaydetme
        if user_message.startswith("/saveword"):
            # ... (kelime kaydetme mantığı aynı)
            parts = user_message.split(" ", 2)
            if len(parts) >= 2:
                word = parts[1]
                meaning = parts[2] if len(parts) > 2 else None
                result = self.save_word(word, meaning)
                return {"type": "saveword", "data": result}
            else:
                return {"error": "Kullanım: /saveword <kelime> [anlam]"}

        # 🔹 Not kaydetme
        if user_message.startswith("/savenote"):
            # ... (not kaydetme mantığı aynı)
            note_text = user_message.replace("/savenote", "", 1).strip()
            if note_text:
                result = self.save_note(note_text)
                return {"type": "savenote", "data": result}
            else:
                return {"error": "Not boş olamaz"}

        # 🔹 Kelime notlarını listeleme - list_words tipini kullanır
        if "kelime notlarımı getir" in user_message.lower():
            # Doğru listenin ve tipin döndürülmesini sağlar
            return {"type": "list_words", "data": self.list_words()}

        # 🔹 Genel notları listeleme - list_notes tipini kullanır
        if "notlarımı getir" in user_message.lower():
            # Doğru listenin ve tipin döndürülmesini sağlar
            return {"type": "list_notes", "data": self.list_notes()}

        # 🔹 Normal chat akışı (OpenAI API çağrısı)
        self.messages.append({"role": "user", "content": user_message})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )

            answer = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": answer})
            return {"type": "chat", "data": answer}

        except Exception as e:
            return {"error": f"Hata: {str(e)}"}


chatbot_instance = EduChatbot()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # ... (kod aynı)
    global chatbot_instance
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"})

    response = chatbot_instance.chat(user_message)

    stats = {
        "notes": len(chatbot_instance.user_data["notes"]),
        "words": len(chatbot_instance.user_data["words"])
    }

    return jsonify({"response": response, "stats": stats})


if __name__ == "__main__":
    print("🌐 Eğitim Chatbotu başlatılıyor...")
    print("http://localhost:5000 adresine gidin")
    app.run(debug=True, host="0.0.0.0", port=5000)