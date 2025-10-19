# 📚 Mini RAG Chat Demo (Spor, Kültür ve Ekonomi)

Bu proje, Streamlit ve ChromaDB'yi kullanarak, bir Büyük Dil Modelini (LLM - OpenAI) özel PDF belgeleriyle güçlendiren basit bir RAG (Retrieval-Augmented Generation) sisteminin demosu dur.

Sistem, kullanıcının sorduğu soruyu, önceden yüklenmiş Spor, Kültür ve Ekonomi konulu PDF belgeleriyle eşleştirir ve bulduğu en alakalı bağlamı (context) kullanarak LLM'den hedefli bir yanıt oluşturmasını ister.

## 🚀 Kurulum ve Başlatma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Ön Gereksinimler

Python 3.8+

pip (Python paket yöneticisi)

### 2. Bağımlılıkları Yükleme

Proje, temel olarak aşağıdaki kütüphaneleri kullanır:

streamlit (Arayüz için)

python-dotenv (API anahtarını yüklemek için)

chromadb (Vektör Veritabanı için)

sentence-transformers (Metinleri vektöre dönüştürmek için)

PyPDF2 (PDF okuma için)

openai (LLM ile yanıt oluşturma için)

Tüm bağımlılıkları tek seferde yüklemek için:

pip install streamlit python-dotenv chromadb sentence-transformers PyPDF2 openai


### 3. Klasör Yapısı

Proje dosyalarınızın aşağıdaki yapıda olduğundan emin olun:

hafta_4-rag-system/
├── pdfs/
│   ├── pdf1.pdf  (Spor içeriği)
│   ├── pdf2.pdf  (Kültür içeriği)
│   └── pdf3.pdf  (Ekonomi içeriği)
├── src/
│   ├── rag_system.py       (RAG pipeline çekirdeği)
│   └── simple_rag_demo.py  (Streamlit arayüzü)
└── .env (OpenAI anahtarı için)


### 4. API Anahtarını Ayarlama

OpenAI API anahtarınızı (GPT modelini kullanmak isterseniz) projenin ana dizininde bulunan .env dosyasına kaydedin.

#### .env dosyası
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


(Not: Bu anahtar olmazsa bile demo çalışır, ancak LLM yerine sadece bağlamı gösteren demo yanıtı alırsınız.)

### 5. Çalıştırma

Terminalinizde src klasörüne gidin ve Streamlit uygulamasını başlatın:

cd src
streamlit run simple_rag_demo.py


Tarayıcınız otomatik olarak açılacak ve RAG uygulamasını kullanmaya başlayabileceksiniz.

### 💡 Nasıl Çalışır?

rag_system.py başlatıldığında:

PDF'leri okur, metinleri 300 karakterlik parçalara (chunk) ayırır.

Her parçayı all-MiniLM-L6-v2 modeliyle bir vektöre dönüştürür ve ChromaDB'ye kaydeder.

Kullanıcı bir soru sorduğunda:

Sorgu vektörleştirilir ve ChromaDB'de en yakın metin parçası bulunur (Retrieval).

Eğer "OpenAI ile yanıt oluştur" seçeneği işaretliyse:

Bulunan bu metin, özel bir talimatla birlikte GPT-3.5-turbo modeline gönderilir.

LLM, sadece bu sağlanan bağlamı kullanarak yanıtı oluşturur (Generation).

### 🛠️ Temel Bileşenler

rag_system.py: Veritabanı kurulumu (ChromaDB), PDF okuma, Chunking, Vektörleştirme, Bağlam Arama ve OpenAI ile yanıt oluşturma mantığını içerir.

simple_rag_demo.py: Kullanıcıdan sorgu alan ve sonuçları gösteren Streamlit web arayüzünü tanımlar.