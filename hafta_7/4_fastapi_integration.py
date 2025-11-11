"""
Frontend-Backend Entegrasyonu
Gradio ve Streamlit ile FastAPI backend entegrasyonu
"""

import gradio as gr
import streamlit as st
import requests
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Environment variables yükle
load_dotenv()

# Backend API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ============================================================================
# GRADIO + FASTAPI ENTEGRASYONU
# ============================================================================

def gradio_chat_with_api(message, history):
    """
    Gradio chatbot - FastAPI backend kullanarak
    """
    try:
        # API'ye istek gönder
        response = requests.post(
            f"{API_BASE_URL}/chat/simple",
            params={"message": message, "model": "gpt-3.5-turbo"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "Yanıt alınamadı")
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Backend API'ye bağlanılamadı. API'nin çalıştığından emin olun."
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def gradio_summarize_with_api(text):
    """
    Gradio metin özetleme - FastAPI backend kullanarak
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/text/summarize",
            params={"text": text, "model": "gpt-3.5-turbo"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("summary", "Özet oluşturulamadı")
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Backend API'ye bağlanılamadı. API'nin çalıştığından emin olun."
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def gradio_translate_with_api(text, target_language):
    """
    Gradio metin çeviri - FastAPI backend kullanarak
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/text/translate",
            params={"text": text, "target_language": target_language, "model": "gpt-3.5-turbo"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("translation", "Çeviri yapılamadı")
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Backend API'ye bağlanılamadı. API'nin çalıştığından emin olun."
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def create_gradio_integration():
    """
    Gradio arayüzü - FastAPI backend ile
    """
    with gr.Blocks(title="Gradio + FastAPI Entegrasyonu") as demo:
        gr.Markdown(
            """
            # 🤖 Gradio + FastAPI Entegrasyonu
            
            Bu uygulama Gradio frontend'i ile FastAPI backend'ini birleştirir.
            """
        )
        
        with gr.Tabs():
            # TAB 1: Chatbot
            with gr.Tab("💬 Chatbot"):
                gr.Markdown("### FastAPI backend ile chatbot")
                chatbot = gr.Chatbot(label="Konuşma")
                msg = gr.Textbox(
                    label="Mesajınız",
                    placeholder="Mesajınızı yazın...",
                    lines=2
                )
                submit_btn = gr.Button("Gönder", variant="primary")
                clear_btn = gr.Button("Temizle")
                
                def respond(message, chat_history):
                    bot_message = gradio_chat_with_api(message, chat_history)
                    chat_history.append((message, bot_message))
                    return "", chat_history
                
                msg.submit(respond, [msg, chatbot], [msg, chatbot])
                submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
                clear_btn.click(lambda: None, None, chatbot, queue=False)
            
            # TAB 2: Metin İşleme
            with gr.Tab("📝 Metin İşleme"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Metin Özetleme")
                        text_input = gr.Textbox(
                            label="Metin",
                            placeholder="Özetlemek istediğiniz metni yazın...",
                            lines=5
                        )
                        summarize_btn = gr.Button("Özetle", variant="primary")
                        summary_output = gr.Textbox(label="Özet", lines=5)
                        
                        summarize_btn.click(gradio_summarize_with_api, text_input, summary_output)
                    
                    with gr.Column():
                        gr.Markdown("### Metin Çeviri")
                        translate_input = gr.Textbox(
                            label="Çevrilecek Metin",
                            placeholder="Çevirmek istediğiniz metni yazın...",
                            lines=3
                        )
                        language_select = gr.Dropdown(
                            choices=["İngilizce", "Fransızca", "Almanca", "İspanyolca", "Japonca"],
                            label="Hedef Dil",
                            value="İngilizce"
                        )
                        translate_btn = gr.Button("Çevir", variant="primary")
                        translate_output = gr.Textbox(label="Çeviri", lines=5)
                        
                        translate_btn.click(gradio_translate_with_api, [translate_input, language_select], translate_output)
        
        gr.Markdown(
            f"""
            ---
            **Backend API URL**: `{API_BASE_URL}`
            
            **Not**: Backend API'nin çalıştığından emin olun:
            ```bash
            uvicorn 3_fastapi_backend:app --reload
            ```
            """
        )
    
    return demo


# ============================================================================
# STREAMLIT + FASTAPI ENTEGRASYONU
# ============================================================================

def streamlit_chat_with_api(message: str) -> str:
    """
    Streamlit chatbot - FastAPI backend kullanarak
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/simple",
            params={"message": message, "model": "gpt-3.5-turbo"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "Yanıt alınamadı")
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Backend API'ye bağlanılamadı. API'nin çalıştığından emin olun."
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def streamlit_summarize_with_api(text: str) -> str:
    """
    Streamlit metin özetleme - FastAPI backend kullanarak
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/text/summarize",
            params={"text": text, "model": "gpt-3.5-turbo"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("summary", "Özet oluşturulamadı")
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Backend API'ye bağlanılamadı. API'nin çalıştığından emin olun."
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def streamlit_translate_with_api(text: str, target_language: str) -> str:
    """
    Streamlit metin çeviri - FastAPI backend kullanarak
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/text/translate",
            params={"text": text, "target_language": target_language, "model": "gpt-3.5-turbo"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("translation", "Çeviri yapılamadı")
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Backend API'ye bağlanılamadı. API'nin çalıştığından emin olun."
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def create_streamlit_integration():
    """
    Streamlit arayüzü - FastAPI backend ile
    """
    st.set_page_config(
        page_title="Streamlit + FastAPI Entegrasyonu",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Streamlit + FastAPI Entegrasyonu")
    st.markdown("Bu uygulama Streamlit frontend'i ile FastAPI backend'ini birleştirir.")
    
    # API durumu kontrolü
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success(f"✅ Backend API çalışıyor: {API_BASE_URL}")
        else:
            st.error(f"❌ Backend API yanıt vermiyor: {health_response.status_code}")
    except Exception:
        st.error(f"❌ Backend API'ye bağlanılamadı: {API_BASE_URL}")
        st.info("Backend API'yi başlatmak için: `uvicorn 3_fastapi_backend:app --reload`")
    
    # Tab yapısı
    tab1, tab2, tab3 = st.tabs(["💬 Chatbot", "📝 Metin İşleme", "📊 API Durumu"])
    
    with tab1:
        st.header("💬 Chatbot")
        st.markdown("### FastAPI backend ile chatbot")
        
        # Mesaj geçmişi
        if "integration_messages" not in st.session_state:
            st.session_state.integration_messages = []
        
        for message in st.session_state.integration_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Yeni mesaj input
        if prompt := st.chat_input("Mesajınızı yazın..."):
            # Kullanıcı mesajını ekle
            st.session_state.integration_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Bot yanıtını al ve göster
            with st.chat_message("assistant"):
                with st.spinner("Yanıt bekleniyor..."):
                    response = streamlit_chat_with_api(prompt)
                    st.markdown(response)
                    st.session_state.integration_messages.append({"role": "assistant", "content": response})
        
        # Temizle butonu
        if st.button("🗑️ Geçmişi Temizle"):
            st.session_state.integration_messages = []
            st.rerun()
    
    with tab2:
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
                        summary = streamlit_summarize_with_api(text_input)
                        st.text_area("Özet:", value=summary, height=150)
                else:
                    st.warning("Lütfen metin girin!")
        
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
                        translation = streamlit_translate_with_api(translate_input, target_language)
                        st.text_area("Çeviri:", value=translation, height=150)
                else:
                    st.warning("Lütfen metin girin!")
    
    with tab3:
        st.header("📊 API Durumu")
        st.markdown("### Backend API bilgileri")
        
        # API endpoint'lerini test et
        endpoints = [
            ("GET /health", "/health"),
            ("POST /chat/simple", "/chat/simple"),
            ("POST /text/summarize", "/text/summarize"),
            ("POST /text/translate", "/text/translate"),
        ]
        
        for method_path, endpoint in endpoints:
            with st.expander(f"{method_path}"):
                if st.button(f"Test {method_path}", key=endpoint):
                    try:
                        if "GET" in method_path:
                            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                        else:
                            response = requests.post(
                                f"{API_BASE_URL}{endpoint}",
                                params={"message": "test", "text": "test", "target_language": "İngilizce"},
                                timeout=5
                            )
                        
                        if response.status_code == 200:
                            st.success(f"✅ Başarılı: {response.status_code}")
                            st.json(response.json())
                        else:
                            st.error(f"❌ Hata: {response.status_code}")
                            st.text(response.text)
                    except Exception as e:
                        st.error(f"❌ Bağlantı hatası: {str(e)}")
        
        st.markdown(f"**API Base URL**: `{API_BASE_URL}`")
        st.markdown("**API Dokümantasyonu**: `/docs` endpoint'inde Swagger UI mevcut")


# ============================================================================
# UYGULAMA ÇALIŞTIRMA
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "gradio":
        # Gradio arayüzünü başlat
        demo = create_gradio_integration()
        demo.queue()
        demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
    else:
        # Streamlit arayüzünü başlat
        create_streamlit_integration()
        
        # Streamlit'i çalıştırmak için:
        # streamlit run 4_fastapi_integration.py

