# 🎓 Eğitim Chatbotu

Eğitim Chatbotu, kullanıcıların **notlarınızı** ve **yabancı dil kelime notlarınızı** kolayca kaydedebildiği, aynı zamanda sohbet ederek dil öğreniminde destek alabileceği bir Flask tabanlı web uygulamasıdır.

---

## 🚀 Özellikler

* 📌 Genel notlarınızı kaydedebilir ve listeleyebilirsiniz.
* 📖 Yeni kelimeleri ve anlamlarını kaydedebilir, listeleyebilirsiniz.
* 🤖 OpenAI tabanlı chatbot entegrasyonu ile dil öğreniminde destek.
* 📝 Kullanıcı dostu arayüz.

---

## 🛠 Teknolojiler

* **Python 3.9+**
* **Flask** (Backend)
* **OpenAI API** (Chatbot için)
* **HTML, CSS, JavaScript** (Frontend)

---

## ⚙️ Gereksinimler

* Python 3.9 veya üstü
* OpenAI API Key (ücretsiz veya ücretli hesap üzerinden alınabilir)

---

## 🔧 Kurulum

### 1. Repo’yu klonlayın

```bash
git clone https://github.com/kullanici/egitim-chatbotu.git
cd egitim-chatbotu
```

### 2. Sanal ortam oluşturun ve bağımlılıkları yükleyin

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. `.env` dosyası oluşturun

Projenizin kök dizininde `.env` dosyası açın ve içine şu satırı ekleyin:

```env
OPENAI_API_KEY=your_api_key_here
```

### 4. Uygulamayı çalıştırın

```bash
python app.py
```

### 5. Tarayıcıdan açın

```
http://localhost:5000
```

---

## 📌 Kullanım

### Komutlar

* `/savenote <not içeriği>` → Genel not ekler.
* `/saveword <kelime> [anlam]` → Kelime notu ekler.
* `notlarımı getir` → Kayıtlı genel notları listeler.
* `kelime notlarımı getir` → Kayıtlı kelime notlarını listeler.

### Arayüz

* 💬 Sohbet kutusundan bot ile etkileşim kurabilirsiniz.
* 📝 "Notlarım" kutucuğu → kayıtlı notları getirir.
* 📖 "Kelime Notları" kutucuğu → kayıtlı kelimeleri getirir.
