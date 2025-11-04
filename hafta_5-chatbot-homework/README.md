# LingoMind — Personal English Vocabulary Coach

🧠 **LingoMind**, kişisel seviyenize ve ilgi alanınıza göre İngilizce kelime öğrenmenizi kolaylaştıran bir uygulamadır. Günlük kelime önerileri, mini konuşma alıştırmaları ve quiz ile dil becerilerinizi geliştirebilirsiniz.

---

## Özellikler

- **Kişisel Profil & Seviye:**  
  Kullanıcı adı, CEFR seviyesi (A1–C1), ilgi alanı ve isteğe bağlı e-posta ile kişiselleştirilmiş deneyim.

- **Günün Kelimeleri:**  
  Günlük 1–3 kelime önerisi, kısa anlam ve örnek cümle ile öğrenme fırsatı.

- **Pratik & Düzeltme:**  
  Kelimeyi kullanarak cümle yazabilir, LLM destekli geri bildirim ile doğru kullanımını öğrenebilirsiniz.

- **Mini Speaking Mode:**  
  Kelimeye dayalı kısa konuşma alıştırmaları. Örnek cümleleri sesli dinleme (TTS).

- **Quiz Modülü:**  
  MCQ ve fill-in-the-blank sorularla kelime bilgisi testi. Sonuçlar kaydedilir ve CSV olarak indirilebilir.

- **Raporlar & Dışa Aktarım:**  
  - Haftalık öğrenilen kelime sayısı  
  - Zorlanılan kelimeler  
  - Quiz başarı oranı  
  - Kullanıcı kelime günlüğü CSV olarak indirilebilir  

---

## Kurulum

1. **Repo’yu klonlayın:**

   git clone <repo-url>
   cd <repo-folder>


2. **Sanal ortam oluşturun ve aktif edin:**
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows


3. **Gerekli paketleri yükleyin:**

pip install -r requirements.txt


4. **.env dosyasını oluşturun ve OpenAI API anahtarınızı ekleyin:**

OPENAI_API_KEY=your_api_key_here


5. **Uygulamayı başlatın:**

streamlit run app.py


## Kullanım

- Profil Oluşturun:

Sol panelden isim, seviye ve ilgi alanınızı girin.


- Günün Kelimelerini Alın:

Profil kaydedildikten sonra kelime önerilerini alabilirsiniz.


- Pratik Yapın:

Kelimeleri kullanarak cümle yazın ve Kontrol et & düzelt butonuyla geri bildirim alın.


- Mini Speaking:

Kelimeyi seçip kısa konuşma alıştırması yapın, örnek cümleyi sesli dinleyin.


- Quiz:

Günün kelimeleri veya geçmiş kelimelerden quiz oluşturun. Cevaplarınız kaydedilir ve detaylı rapor alabilirsiniz.


- Raporlar & Dışa Aktarım:

Sağ sütundan haftalık özet, quiz raporu ve kelime günlüğünü CSV olarak indirebilirsiniz.


#### Lisans

Bu proje demo amaçlıdır. Ticari kullanım için uygun değildir.


