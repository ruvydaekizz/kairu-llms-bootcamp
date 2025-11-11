# Hafta 7: LLM Tabanlı Uygulama Dağıtımı

Bu hafta **LLM tabanlı uygulamaları** production ortamına dağıtmayı öğreneceksiniz. Frontend (Gradio/Streamlit), Backend (FastAPI) ve Deployment (Docker) konularında derinlemesine bilgi edineceksiniz.

## 📋 İçerik

### 🎨 1. Gradio ile Frontend (`1_gradio_frontend.py`)
- **Temel Gradio Yapısı**: Basit chatbot arayüzü
- **Gelişmiş Özellikler**: Dosya yükleme, görüntü işleme, tablo gösterimi
- **Streaming Output**: Real-time cevaplar
- **Custom Styling**: Özelleştirilmiş arayüz tasarımı
- **Multi-Modal Inputs**: Metin, görüntü, ses desteği

**Öğrenecekleriniz:**
- Gradio ile hızlı prototipleme
- Kullanıcı dostu arayüzler oluşturma
- Streaming ve real-time feedback
- Multi-modal uygulamalar geliştirme

### 🌊 2. Streamlit ile Frontend (`2_streamlit_frontend.py`)
- **Temel Streamlit Yapısı**: Basit chatbot uygulaması
- **Widgets ve Etkileşimler**: Slider, selectbox, text input
- **Session State**: Kullanıcı durumu yönetimi
- **Data Visualization**: Grafikler ve tablolar
- **Sidebar ve Layout**: Profesyonel düzenleme

**Öğrenecekleriniz:**
- Streamlit ile interaktif uygulamalar
- State yönetimi ve kullanıcı deneyimi
- Veri görselleştirme entegrasyonu
- Modern web arayüzleri tasarlama

### 🚀 3. FastAPI ile Backend (`3_fastapi_backend.py`)
- **Temel FastAPI Yapısı**: Basit API endpoint'leri
- **LLM Entegrasyonu**: OpenAI ve Hugging Face modelleri
- **Request/Response Modelleri**: Pydantic ile veri doğrulama
- **Error Handling**: Hata yönetimi ve validasyon
- **Async Operations**: Asenkron işlemler

**Öğrenecekleriniz:**
- RESTful API tasarımı
- FastAPI ile hızlı backend geliştirme
- LLM model entegrasyonu
- Async programlama ve performans

### 🔗 4. Frontend-Backend Entegrasyonu (`4_fastapi_integration.py`)
- **Gradio + FastAPI**: Frontend ile backend bağlantısı
- **Streamlit + FastAPI**: Tam entegrasyon örneği
- **Authentication**: API key yönetimi
- **Rate Limiting**: İstek sınırlama
- **CORS Yapılandırması**: Cross-origin istekleri

**Öğrenecekleriniz:**
- Frontend ve backend arası iletişim
- API authentication ve güvenlik
- Production-ready uygulamalar
- End-to-end sistem tasarımı

### 🐳 5. Docker ve Deployment (`5_docker_setup.py` + Dockerfile)
- **Docker Temelleri**: Container yapısı
- **Dockerfile Oluşturma**: Image build etme
- **Docker Compose**: Multi-container uygulamalar
- **Environment Variables**: Güvenli yapılandırma
- **Production Deployment**: Cloud deployment stratejileri

**Öğrenecekleriniz:**
- Docker ile containerization
- Production deployment süreçleri
- Environment yönetimi
- Cloud platformlarına dağıtım

## 🚀 Kurulum

### 1. Virtual Environment Oluştur
```bash
# Virtual environment oluştur
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux  
source venv/bin/activate
```

### 2. Paketleri Yükle
```bash
pip install -r requirements.txt
```

### 3. Environment Değişkenlerini Ayarla
`.env` dosyası oluşturun:
```
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
```

### 4. Test Et
```bash
# Gradio test
python 1_gradio_frontend.py

# Streamlit test
streamlit run 2_streamlit_frontend.py

# FastAPI test
uvicorn 3_fastapi_backend:app --reload

# Docker test
docker build -t llm-app .
docker run -p 8000:8000 llm-app
```

## 📚 Dosya Açıklamaları

| Dosya | Açıklama |
|-------|----------|
| `1_gradio_frontend.py` | Gradio ile frontend uygulaması |
| `2_streamlit_frontend.py` | Streamlit ile frontend uygulaması |
| `3_fastapi_backend.py` | FastAPI ile backend API |
| `4_fastapi_integration.py` | Frontend-Backend entegrasyonu |
| `5_docker_setup.py` | Docker yapılandırma scripti |
| `Dockerfile` | Docker image yapılandırması |
| `docker-compose.yml` | Multi-container yapılandırması |
| `requirements.txt` | Gerekli paketler |
| `.dockerignore` | Docker build ignore listesi |

## 🎓 Çalışma Sırası

1. **Gradio ile başlayın** (`1_gradio_frontend.py`) - Hızlı prototipleme
2. **Streamlit'i deneyin** (`2_streamlit_frontend.py`) - İnteraktif uygulamalar
3. **FastAPI backend'i öğrenin** (`3_fastapi_backend.py`) - API geliştirme
4. **Entegrasyonu yapın** (`4_fastapi_integration.py`) - Tam sistem
5. **Docker ile deploy edin** (`5_docker_setup.py`) - Production hazırlığı

## 🔧 Önemli Konseptler

### Frontend Framework'leri
- **Gradio**: Hızlı prototipleme, minimal kod
- **Streamlit**: Data science odaklı, interaktif widget'lar
- **Her ikisi de**: Otomatik UI, Python tabanlı

### Backend API
- **FastAPI**: Modern, hızlı, async destekli
- **RESTful**: Standart HTTP metodları
- **Pydantic**: Veri doğrulama ve serialization

### Deployment
- **Docker**: Containerization, izolasyon
- **Docker Compose**: Multi-container orchestration
- **Environment Variables**: Güvenli yapılandırma

## 🐛 Sorun Giderme

### Port Hatası
```
Error: Port 8000 already in use
```
**Çözüm**: Farklı bir port kullanın veya mevcut process'i durdurun
```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### API Key Hatası
```
Error: API key not found
```
**Çözüm**: `.env` dosyasında API anahtarınızı kontrol edin

### Docker Build Hatası
```
Error: Cannot connect to Docker daemon
```
**Çözüm**: Docker Desktop'ın çalıştığından emin olun

### Import Hatası
```
ImportError: No module named 'gradio'
```
**Çözüm**: Virtual environment aktif mi kontrol edin, requirements.txt yükleyin

## 📊 Performans İpuçları

### Frontend Optimizasyonu
- Gradio için `queue()` kullanarak rate limiting yapın
- Streamlit için `@st.cache` ile caching kullanın
- Gereksiz widget'ları kaldırın

### Backend Optimizasyonu
- Async/await kullanarak concurrent işlemler yapın
- Connection pooling kullanın
- Rate limiting implementasyonu yapın

### Docker Optimizasyonu
- Multi-stage builds kullanın
- .dockerignore ile gereksiz dosyaları hariç tutun
- Layer caching'i optimize edin

## 🎯 Ödev Hazırlığı

Ödev için aşağıdaki konuları anladığınızdan emin olun:

1. **Frontend Seçimi**: Gradio mu Streamlit mi? Ne zaman hangisini kullanırsınız?
2. **API Tasarımı**: RESTful API nasıl tasarlanır?
3. **Docker Containerization**: Uygulamanızı nasıl containerize edersiniz?
4. **Deployment**: Production ortamına nasıl deploy edersiniz?

## 📖 Ek Kaynaklar

- [Gradio Documentation](https://www.gradio.app/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)

## 💡 İpuçları

- Her örneği adım adım çalıştırın
- Kod üzerinde değişiklikler yaparak deneyin
- API endpoint'lerini test etmek için Postman veya curl kullanın
- Docker image'larını optimize edin
- Environment variable'ları güvenli tutun
- Production'da logging ve monitoring ekleyin

## 🌐 Deployment Platformları

### Ücretsiz Seçenekler
- **Hugging Face Spaces**: Gradio ve Streamlit için
- **Render**: Full-stack uygulamalar için
- **Railway**: Docker desteği ile
- **Fly.io**: Global deployment

### Ücretli Seçenekler
- **AWS**: EC2, ECS, Lambda
- **Google Cloud**: Cloud Run, GKE
- **Azure**: Container Instances, AKS
- **DigitalOcean**: App Platform, Droplets

**Başarılar! 🚀**

