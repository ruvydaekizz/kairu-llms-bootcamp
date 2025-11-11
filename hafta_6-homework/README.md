# Movie Sentiment Classifier

Bu proje, IMDb puanlarına göre film metinlerini (movie_title + overview) sınıflandırmak için bir **DistilBERT tabanlı Transformer model** kullanmaktadır.  

Proje iki ana bölümden oluşur:
1. **Datasets + Trainer**: CSV verisini yükler, label oluşturur, tokenization ve eğitim sürecini yürütür.
2. **Inference ve Kişiselleştirilmiş Model Kullanımı**: Eğitilmiş modeli yükler, tekli veya batch sınıflandırma yapar, değerlendirme raporu oluşturur ve kullanıcı profiline özel prompt oluşturabilir.

---

## Özellikler

- CSV dosyasından otomatik text ve label kolonlarını algılar (`movie_title` + `imdb_score` varsayılan)
- IMDb puanını binary label’a dönüştürür (otomatik threshold seçimi destekli)
- Training seti dengelenir (undersample)
- Tokenization sırasında label `labels` olarak rename edilir
- Modern ve legacy `TrainingArguments` uyumluluğu
- Eğitilmiş model `./fine_tuned_model` dizinine kaydedilir
- Tek örnek veya batch sınıflandırma
- Confusion matrix ve classification report
- Kişiselleştirilmiş prompt oluşturma

---

## Kurulum


#### Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

#### Gereksinimleri yükle
pip install -r requirements.txt



## Kullanım

1. Eğitim

python 2_datasets_trainer1.py

Model ./fine_tuned_model klasörüne kaydedilir.

Eğitim sonunda eval seti üzerindeki metrikler görüntülenir.



2. Inference ve Değerlendirme

python 3_inference_personalization1.py

Tek bir örnek veya batch örnekler için sınıflandırma yapılabilir.

CSV üzerindeki tüm dataset için confusion matrix ve classification report oluşturulur.

Kullanıcı profiline özel prompt üretilebilir.


project/
│
├─ data/
│   └─ movie_metadata.csv
├─ fine_tuned_model/    # Eğitilmiş model burada
├─ 2_datasets_trainer1.py
├─ 3_inference_personalization1.py
├─ requirements.txt
├─ .gitignore
└─ README.md


