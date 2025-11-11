"""
Gradio ile Frontend Uygulaması
LLM tabanlı chatbot ve çeşitli uygulamalar için Gradio arayüzü
"""

import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Environment variables yükle
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# ÖRNEK 1: Basit Chatbot Arayüzü
# ============================================================================

def simple_chatbot(message, history):
    """
    Basit chatbot fonksiyonu
    """
    try:
        # Convert history to OpenAI format
        messages = [{"role": "system", "content": "Sen yardımcı bir asistansın. Kısa ve net cevaplar ver."}]
        
        # Add conversation history if it exists
        if history:
            for msg in history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append(msg)
                elif isinstance(msg, (list, tuple)) and len(msg) == 2:
                    # Handle old tuple format if any
                    messages.append({"role": "user", "content": msg[0]})
                    messages.append({"role": "assistant", "content": msg[1]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


# ============================================================================
# ÖRNEK 2: Streaming Output ile Chatbot
# ============================================================================

def streaming_chatbot(message, history):
    """
    Streaming output ile chatbot
    """
    try:
        # Convert history to OpenAI format
        messages = [{"role": "system", "content": "Sen yardımcı bir asistansın."}]
        
        # Add conversation history if it exists
        if history:
            for msg in history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append(msg)
                elif isinstance(msg, (list, tuple)) and len(msg) == 2:
                    # Handle old tuple format if any
                    messages.append({"role": "user", "content": msg[0]})
                    messages.append({"role": "assistant", "content": msg[1]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
            max_tokens=200,
            temperature=0.7
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                yield full_response
    except Exception as e:
        yield f"Hata oluştu: {str(e)}"


# ============================================================================
# ÖRNEK 3: Metin İşleme Uygulaması
# ============================================================================

def text_summarizer(text):
    """
    Metin özetleme fonksiyonu
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen bir metin özetleme uzmanısın. Verilen metni kısa ve öz şekilde özetle."},
                {"role": "user", "content": f"Bu metni özetle:\n\n{text}"}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


def text_translator(text, target_language):
    """
    Metin çeviri fonksiyonu
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Sen bir çevirmensin. Verilen metni {target_language} diline çevir."},
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


# ============================================================================
# ÖRNEK 4: Multi-Input Uygulaması
# ============================================================================

def code_explainer(code, language):
    """
    Kod açıklama fonksiyonu
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Sen bir {language} programlama uzmanısın. Verilen kodu detaylı şekilde açıkla."},
                {"role": "user", "content": f"Bu kodu açıkla:\n\n```{language}\n{code}\n```"}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


# ============================================================================
# ÖRNEK 5: Dosya Yükleme ve İşleme
# ============================================================================

def file_processor(file):
    """
    Dosya içeriğini işleme (PDF, metin dosyaları vb.)
    """
    if file is None:
        return "Lütfen bir dosya yükleyin."
    
    try:
        # Dosya yolunu al
        file_path = file.name if hasattr(file, 'name') else file
        
        # Dosya adını ve uzantısını al
        import os
        filename = os.path.basename(file_path)
        file_extension = os.path.splitext(filename)[1].lower()
        
        content = ""
        
        # PDF dosyaları için
        if file_extension == '.pdf':
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages[:5]:  # İlk 5 sayfa
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n\n"
                
                if not content:
                    # Alternatif olarak PyPDF2 dene
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page_num in range(min(5, len(pdf_reader.pages))):
                            page = pdf_reader.pages[page_num]
                            content += page.extract_text() + "\n\n"
                            
            except Exception as pdf_error:
                return f"PDF okuma hatası: {str(pdf_error)}"
        
        # Metin dosyaları için
        else:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
        
        if not content:
            return "Dosya okunamadı. Desteklenmeyen format veya karakter kodlaması."
        
        # İlk 2000 karakteri al (API limiti için)
        content_preview = content[:2000]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen bir dosya analiz uzmanısın. Verilen dosya içeriğini analiz et, özetini çıkar ve ana konuları belirt."},
                {"role": "user", "content": f"Dosya adı: {filename}\nDosya tipi: {file_extension}\n\nDosya içeriğini analiz et:\n\n{content_preview}"}
            ],
            max_tokens=400,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"


# ============================================================================
# GRADIO ARAYÜZÜ OLUŞTURMA
# ============================================================================

def create_gradio_interface():
    """
    Gradio arayüzünü oluştur
    """
    
    # Tema ve stil ayarları
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        font=("Arial", "sans-serif")
    )
    
    with gr.Blocks(theme=theme, title="LLM Uygulama Demo") as demo:
        gr.Markdown(
            """
            # 🤖 LLM Tabanlı Uygulama Örnekleri
            
            Bu uygulama Gradio kullanarak çeşitli LLM uygulamalarını gösterir.
            """
        )
        
        # Tab yapısı
        with gr.Tabs():
            # TAB 1: Basit Chatbot
            with gr.Tab("💬 Basit Chatbot"):
                gr.Markdown("### Basit chatbot arayüzü")
                chatbot = gr.Chatbot(label="Konuşma", type="messages")
                msg = gr.Textbox(
                    label="Mesajınız",
                    placeholder="Mesajınızı yazın...",
                    lines=2
                )
                submit_btn = gr.Button("Gönder", variant="primary")
                clear_btn = gr.Button("Temizle")
                
                def respond(message, chat_history):
                    bot_message = simple_chatbot(message, chat_history)
                    chat_history.append({"role": "user", "content": message})
                    chat_history.append({"role": "assistant", "content": bot_message})
                    return "", chat_history
                
                msg.submit(respond, [msg, chatbot], [msg, chatbot])
                submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
                clear_btn.click(lambda: [], None, chatbot, queue=False)
            
            # TAB 2: Streaming Chatbot
            with gr.Tab("🌊 Streaming Chatbot"):
                gr.Markdown("### Streaming output ile chatbot")
                streaming_chatbot_ui = gr.Chatbot(label="Konuşma", type="messages")
                streaming_msg = gr.Textbox(
                    label="Mesajınız",
                    placeholder="Mesajınızı yazın...",
                    lines=2
                )
                streaming_submit = gr.Button("Gönder", variant="primary")
                streaming_clear = gr.Button("Temizle")
                
                def streaming_respond(message, chat_history):
                    chat_history.append({"role": "user", "content": message})
                    chat_history.append({"role": "assistant", "content": ""})
                    for response in streaming_chatbot(message, chat_history[:-2]):  # Exclude the current exchange
                        chat_history[-1] = {"role": "assistant", "content": response}
                        yield chat_history
                
                streaming_msg.submit(streaming_respond, [streaming_msg, streaming_chatbot_ui], streaming_chatbot_ui)
                streaming_submit.click(streaming_respond, [streaming_msg, streaming_chatbot_ui], streaming_chatbot_ui)
                streaming_clear.click(lambda: [], None, streaming_chatbot_ui, queue=False)
            
            # TAB 3: Metin İşleme
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
                        
                        summarize_btn.click(text_summarizer, text_input, summary_output)
                    
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
                        
                        translate_btn.click(text_translator, [translate_input, language_select], translate_output)
            
            # TAB 4: Kod Açıklama
            with gr.Tab("💻 Kod Açıklama"):
                gr.Markdown("### Kod açıklama aracı")
                code_input = gr.Code(
                    label="Kod",
                    language="python"
                )
                code_language = gr.Dropdown(
                    choices=["Python", "JavaScript", "Java", "C++", "Go"],
                    label="Programlama Dili",
                    value="Python"
                )
                explain_btn = gr.Button("Açıkla", variant="primary")
                code_explanation = gr.Textbox(label="Açıklama", lines=10)
                
                explain_btn.click(code_explainer, [code_input, code_language], code_explanation)
            
            # TAB 5: Dosya İşleme
            with gr.Tab("📁 Dosya İşleme"):
                gr.Markdown("### Dosya içeriği analizi\nDesteklenen formatlar: PDF, TXT, Python, JavaScript, Markdown, JSON, CSV, HTML, CSS, YAML, XML")
                file_input = gr.File(
                    label="Dosya Yükle",
                    file_types=[".txt", ".py", ".js", ".md", ".json", ".csv", ".html", ".css", ".yaml", ".yml", ".xml", ".pdf"]
                )
                process_btn = gr.Button("İşle", variant="primary")
                file_output = gr.Textbox(label="Analiz Sonucu", lines=10)
                
                process_btn.click(file_processor, file_input, file_output)
        
        # Footer
        gr.Markdown(
            """
            ---
            **Not**: Bu uygulama OpenAI API kullanmaktadır. API key'inizi `.env` dosyasına eklemeyi unutmayın.
            """
        )
    
    return demo


# ============================================================================
# UYGULAMA ÇALIŞTIRMA
# ============================================================================

if __name__ == "__main__":
    demo = create_gradio_interface()
    
    # Queue kullanarak rate limiting
    demo.queue()
    
    # Uygulamayı başlat
    demo.launch(
        server_name="0.0.0.0",  # Tüm network interface'lerde dinle
        server_port=7861,        # Port numarası
        share=False,             # Public link oluşturma
        show_error=True          # Hataları göster
    )

