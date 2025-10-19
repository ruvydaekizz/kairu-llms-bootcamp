import streamlit as st
# rag_system.py dosyasını aynı dizinde olduğu için doğrudan import ediyoruz.
from rag_system import rag_pipeline 
import os
from dotenv import load_dotenv
import sys

# .env yükle
load_dotenv()

st.set_page_config(page_title="📚 Mini RAG Chat", page_icon="🤖")
st.title("📚 Mini RAG Chat Demo")

st.markdown("""
Bu demo, PDF belgelerinden oluşturulmuş RAG (Retrieval-Augmented Generation) sistemini gösterir.  
Sistem, sorgu ile en alakalı **tek bir metin parçasını** (chunk) bulur ve LLM'i bu bağlamla yanıtlaması için yönlendirir.
""")

# -------------------------------
# Kullanıcı Arayüzü
# -------------------------------
query = st.text_input("Soru sor:")

# OpenAI anahtarı yoksa veya kütüphane yüklü değilse uyarı göster
openai_available = os.getenv('OPENAI_API_KEY') and 'openai' in sys.modules
use_openai = st.checkbox("OpenAI ile yanıt oluştur (Anahtar Gerekli)", value=False, disabled=not openai_available)

if not openai_available:
    st.warning("⚠️ OpenAI API anahtarı (.env dosyasında) veya kütüphanesi (pip install openai) bulunmadığı için LLM ile yanıt oluşturma pasiftir.")

if query:
    st.info("🔍 Sorgu işleniyor...")
    
    # RAG pipeline çalıştır
    result = rag_pipeline(query, use_openai=use_openai)
    
    if result['context']:
        st.subheader("🔍 Retrieval Sonucu (Bağlam)")
        st.write(f"**Belge ID:** {result['context']['id']}")
        st.write(f"**Kategori:** {result['context']['metadata']['category']}")
        st.write(f"**Mesafe Skoru (Düşük İyidir):** {result['context']['score']:.3f}")
        
        # Retrieval text'i genişletilebilir bir alanda göster
        with st.expander("Genişlet: Bulunan Metin Parçası (Context)"):
            st.code(result['context']['text'], language='markdown')
            
    st.subheader("🤖 Yanıt")
    st.markdown(result['response'])

# -------------------------------
# Ek Bilgilendirme
# -------------------------------
st.markdown("""
---
### Sistem Notları
💡 **Kapsam:** Sistem şu anda sadece eklediğiniz PDF belgeleri üzerinden bilgi verir.  
**Score:** Mesafe Skoru. **Daha düşük bir skor** (örneğin 0.0'a yakın) daha iyi bir eşleşme anlamına gelir. 0.5'ten büyük skorlar genellikle "kapsam dışı" kabul edilir.
""")