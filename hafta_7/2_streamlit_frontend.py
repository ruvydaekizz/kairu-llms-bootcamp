"""
Streamlit ile Frontend Uygulaması
LLM tabanlı chatbot ve çeşitli uygulamalar için Streamlit arayüzü
"""

import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import pandas as pd
import plotly.express as px

# Environment variables yükle
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# SAYFA YAPILANDIRMASI
# ============================================================================

st.set_page_config(
    page_title="LLM Uygulama Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SIDEBAR YAPILANDIRMASI
# ============================================================================

with st.sidebar:
    st.title("⚙️ Ayarlar")
    
    # Model seçimi
    model_choice = st.selectbox(
        "Model Seçin:",
        ["gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    
    # Temperature ayarı
    temperature = st.slider(
        "Temperature (Yaratıcılık):",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )
    
    # Max tokens ayarı
    max_tokens = st.slider(
        "Max Tokens (Maksimum uzunluk):",
        min_value=50,
        max_value=500,
        value=150,
        step=50
    )
    
    st.divider()
    
    # API Key kontrolü
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ API Key bulunamadı! `.env` dosyasını kontrol edin.")
    else:
        st.success("✅ API Key yüklendi")
    
    st.divider()
    
    # Temizle butonu
    if st.button("🗑️ Tüm Geçmişi Temizle"):
        st.session_state.messages = []
        st.rerun()

# ============================================================================
# SESSION STATE YÖNETİMİ
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "text_summary" not in st.session_state:
    st.session_state.text_summary = ""

if "translation_result" not in st.session_state:
    st.session_state.translation_result = ""

# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def get_openai_response(prompt, system_prompt="Sen yardımcı bir asistansın.", model="gpt-3.5-turbo"):
    """
    OpenAI API'den yanıt al
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def stream_openai_response(prompt, system_prompt="Sen yardımcı bir asistansın.", model="gpt-3.5-turbo"):
    """
    OpenAI API'den streaming yanıt al
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                yield full_response
    except Exception as e:
        yield f"Hata oluştu: {str(e)}"


# ============================================================================
# ANA SAYFA
# ============================================================================

st.title("🤖 LLM Tabanlı Uygulama Örnekleri")
st.markdown("Bu uygulama Streamlit kullanarak çeşitli LLM uygulamalarını gösterir.")

# Tab yapısı
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chatbot",
    "🌊 Streaming Chatbot",
    "📝 Metin İşleme",
    "💻 Kod Açıklama",
    "📊 Veri Görselleştirme"
])

# ============================================================================
# TAB 1: Basit Chatbot
# ============================================================================

with tab1:
    st.header("💬 Basit Chatbot")
    st.markdown("### Basit chatbot arayüzü")
    
    # Mesaj geçmişini göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Yeni mesaj input
    if prompt := st.chat_input("Mesajınızı yazın..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Bot yanıtını al ve göster
        with st.chat_message("assistant"):
            response = get_openai_response(prompt, model=model_choice)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# ============================================================================
# TAB 2: Streaming Chatbot
# ============================================================================

with tab2:
    st.header("🌊 Streaming Chatbot")
    st.markdown("### Streaming output ile chatbot")
    
    # Streaming mesaj geçmişi
    if "streaming_messages" not in st.session_state:
        st.session_state.streaming_messages = []
    
    for message in st.session_state.streaming_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Yeni mesaj input
    if streaming_prompt := st.chat_input("Mesajınızı yazın... (Streaming)"):
        # Kullanıcı mesajını ekle
        st.session_state.streaming_messages.append({"role": "user", "content": streaming_prompt})
        with st.chat_message("user"):
            st.markdown(streaming_prompt)
        
        # Bot streaming yanıtını al ve göster
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            for chunk in stream_openai_response(streaming_prompt, model=model_choice):
                full_response = chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.streaming_messages.append({"role": "assistant", "content": full_response})
    
    # Temizle butonu
    if st.button("🗑️ Streaming Geçmişini Temizle"):
        st.session_state.streaming_messages = []
        st.rerun()

# ============================================================================
# TAB 3: Metin İşleme
# ============================================================================

with tab3:
    st.header("📝 Metin İşleme")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Metin Özetleme")
        text_input = st.text_area(
            "Özetlemek istediğiniz metni yazın:",
            height=200,
            placeholder="Metninizi buraya yazın..."
        )
        
        if st.button("Özetle", type="primary"):
            if text_input:
                with st.spinner("Özetleme yapılıyor..."):
                    summary = get_openai_response(
                        f"Bu metni özetle:\n\n{text_input}",
                        "Sen bir metin özetleme uzmanısın. Verilen metni kısa ve öz şekilde özetle.",
                        model=model_choice
                    )
                    st.session_state.text_summary = summary
                    st.success("Özetleme tamamlandı!")
        
        if st.session_state.text_summary:
            st.text_area("Özet:", value=st.session_state.text_summary, height=150)
    
    with col2:
        st.subheader("🌍 Metin Çeviri")
        translate_input = st.text_area(
            "Çevirmek istediğiniz metni yazın:",
            height=150,
            placeholder="Çevrilecek metni buraya yazın..."
        )
        
        target_language = st.selectbox(
            "Hedef Dil:",
            ["İngilizce", "Fransızca", "Almanca", "İspanyolca", "Japonca", "Türkçe"]
        )
        
        if st.button("Çevir", type="primary"):
            if translate_input:
                with st.spinner("Çeviri yapılıyor..."):
                    translation = get_openai_response(
                        translate_input,
                        f"Sen bir çevirmensin. Verilen metni {target_language} diline çevir.",
                        model=model_choice
                    )
                    st.session_state.translation_result = translation
                    st.success("Çeviri tamamlandı!")
        
        if st.session_state.translation_result:
            st.text_area("Çeviri:", value=st.session_state.translation_result, height=150)

# ============================================================================
# TAB 4: Kod Açıklama
# ============================================================================

with tab4:
    st.header("💻 Kod Açıklama")
    st.markdown("### Kod açıklama aracı")
    
    code_language = st.selectbox(
        "Programlama Dili:",
        ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
        index=0
    )
    
    code_input = st.text_area(
        "Açıklamak istediğiniz kodu yazın:",
        height=300,
        placeholder=f"# {code_language} kodunuzu buraya yazın..."
    )
    
    if st.button("Açıkla", type="primary"):
        if code_input:
            with st.spinner("Kod açıklaması oluşturuluyor..."):
                explanation = get_openai_response(
                    f"Bu kodu açıkla:\n\n```{code_language.lower()}\n{code_input}\n```",
                    f"Sen bir {code_language} programlama uzmanısın. Verilen kodu detaylı şekilde açıkla.",
                    model=model_choice
                )
                st.success("Açıklama oluşturuldu!")
                st.markdown("### 📖 Açıklama:")
                st.markdown(explanation)
        else:
            st.warning("Lütfen kod girin!")

# ============================================================================
# TAB 5: Veri Görselleştirme
# ============================================================================

with tab5:
    st.header("📊 Veri Görselleştirme")
    st.markdown("### LLM ile veri analizi ve görselleştirme")
    
    # Örnek veri oluştur
    sample_data = {
        "Ürün": ["A", "B", "C", "D", "E"],
        "Satış": [100, 150, 200, 120, 180],
        "Kategori": ["Elektronik", "Giyim", "Elektronik", "Giyim", "Elektronik"]
    }
    df = pd.DataFrame(sample_data)
    
    st.subheader("Örnek Veri")
    st.dataframe(df, width='stretch')
    
    # Veri analizi için prompt
    analysis_prompt = st.text_area(
        "Veri analizi için soru sorun:",
        placeholder="Örn: Bu verilerde hangi kategoride en çok satış var?",
        height=100
    )
    
    if st.button("Analiz Et", type="primary"):
        if analysis_prompt:
            with st.spinner("Analiz yapılıyor..."):
                # Veriyi string'e çevir
                data_str = df.to_string()
                
                response = get_openai_response(
                    f"Bu veri tablosunu analiz et:\n\n{data_str}\n\nSoru: {analysis_prompt}",
                    "Sen bir veri analiz uzmanısın. Verilen veriyi analiz et ve yorum yap.",
                    model=model_choice
                )
                
                st.markdown("### 📊 Analiz Sonucu:")
                st.markdown(response)
                
                # Görselleştirme
                st.markdown("### 📈 Görselleştirme:")
                
                # Bar chart
                fig_bar = px.bar(df, x="Ürün", y="Satış", color="Kategori", title="Ürün Satışları")
                st.plotly_chart(fig_bar, use_columns_width=True)
                
                # Pie chart
                category_sales = df.groupby("Kategori")["Satış"].sum().reset_index()
                fig_pie = px.pie(category_sales, values="Satış", names="Kategori", title="Kategori Bazında Satış Dağılımı")
                st.plotly_chart(fig_pie, use_columns_width=True)
        else:
            st.warning("Lütfen bir soru girin!")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    """
    ---
    **Not**: Bu uygulama OpenAI API kullanmaktadır. API key'inizi `.env` dosyasına eklemeyi unutmayın.
    """
)

