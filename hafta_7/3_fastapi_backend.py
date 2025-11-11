"""
FastAPI ile Backend API
LLM tabanlı uygulamalar için RESTful API
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
import uvicorn
import json
from datetime import datetime

# Environment variables yükle
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# FASTAPI APP OLUŞTURMA
# ============================================================================

app = FastAPI(
    title="LLM Backend API",
    description="LLM tabanlı uygulamalar için RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# CORS YAPILANDIRMASI
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELLERİ
# ============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Mesaj rolü: 'user' veya 'assistant'")
    content: str = Field(..., description="Mesaj içeriği")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Konuşma mesajları")
    model: str = Field(default="gpt-3.5-turbo", description="Kullanılacak model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Yaratıcılık seviyesi")
    max_tokens: int = Field(default=150, ge=1, le=4000, description="Maksimum token sayısı")
    stream: bool = Field(default=False, description="Streaming yanıt isteniyor mu?")


class TextProcessRequest(BaseModel):
    text: str = Field(..., description="İşlenecek metin")
    operation: str = Field(..., description="İşlem türü: 'summarize', 'translate', 'analyze'")
    language: Optional[str] = Field(default=None, description="Hedef dil (çeviri için)")
    model: str = Field(default="gpt-3.5-turbo", description="Kullanılacak model")


class CodeExplainRequest(BaseModel):
    code: str = Field(..., description="Açıklanacak kod")
    language: str = Field(..., description="Programlama dili")
    model: str = Field(default="gpt-3.5-turbo", description="Kullanılacak model")


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_key_configured: bool


# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def get_openai_response(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int):
    """
    OpenAI API'den yanıt al
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API hatası: {str(e)}")


def stream_openai_response(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int):
    """
    OpenAI API'den streaming yanıt al
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


# ============================================================================
# API ENDPOINT'LERİ
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint - API bilgileri
    """
    return {
        "message": "LLM Backend API'ye hoş geldiniz!",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        api_key_configured=bool(os.getenv("OPENAI_API_KEY"))
    )


@app.post("/chat", tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint - Basit chatbot
    """
    try:
        # Mesajları dict formatına çevir
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Streaming isteniyorsa
        if request.stream:
            return StreamingResponse(
                stream_openai_response(messages, request.model, request.temperature, request.max_tokens),
                media_type="text/event-stream"
            )
        
        # Normal yanıt
        response_content = get_openai_response(
            messages,
            request.model,
            request.temperature,
            request.max_tokens
        )
        
        return {
            "response": response_content,
            "model": request.model,
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(str(messages)) + len(response_content.split())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/simple", tags=["Chat"])
async def chat_simple(message: str, model: str = "gpt-3.5-turbo"):
    """
    Basit chat endpoint - Tek mesaj
    """
    try:
        messages = [
            {"role": "system", "content": "Sen yardımcı bir asistansın."},
            {"role": "user", "content": message}
        ]
        
        response_content = get_openai_response(messages, model, 0.7, 150)
        
        return {
            "message": message,
            "response": response_content,
            "model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text/process", tags=["Text Processing"])
async def process_text(request: TextProcessRequest):
    """
    Metin işleme endpoint - Özetleme, çeviri, analiz
    """
    try:
        system_prompts = {
            "summarize": "Sen bir metin özetleme uzmanısın. Verilen metni kısa ve öz şekilde özetle.",
            "translate": f"Sen bir çevirmensin. Verilen metni {request.language or 'İngilizce'} diline çevir.",
            "analyze": "Sen bir metin analiz uzmanısın. Verilen metni analiz et ve yorum yap."
        }
        
        system_prompt = system_prompts.get(
            request.operation,
            "Sen yardımcı bir asistansın."
        )
        
        if request.operation == "translate" and request.language:
            user_prompt = f"Bu metni {request.language} diline çevir:\n\n{request.text}"
        elif request.operation == "summarize":
            user_prompt = f"Bu metni özetle:\n\n{request.text}"
        else:
            user_prompt = f"Bu metni analiz et:\n\n{request.text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_content = get_openai_response(messages, request.model, 0.5, 200)
        
        return {
            "original_text": request.text,
            "operation": request.operation,
            "result": response_content,
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/code/explain", tags=["Code"])
async def explain_code(request: CodeExplainRequest):
    """
    Kod açıklama endpoint
    """
    try:
        system_prompt = f"Sen bir {request.language} programlama uzmanısın. Verilen kodu detaylı şekilde açıkla."
        
        user_prompt = f"Bu kodu açıkla:\n\n```{request.language.lower()}\n{request.code}\n```"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_content = get_openai_response(messages, request.model, 0.5, 300)
        
        return {
            "code": request.code,
            "language": request.language,
            "explanation": response_content,
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text/summarize", tags=["Text Processing"])
async def summarize_text(text: str, model: str = "gpt-3.5-turbo"):
    """
    Hızlı metin özetleme endpoint
    """
    try:
        messages = [
            {"role": "system", "content": "Sen bir metin özetleme uzmanısın. Verilen metni kısa ve öz şekilde özetle."},
            {"role": "user", "content": f"Bu metni özetle:\n\n{text}"}
        ]
        
        response_content = get_openai_response(messages, model, 0.5, 150)
        
        return {
            "original_text": text,
            "summary": response_content,
            "model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/text/translate", tags=["Text Processing"])
async def translate_text(text: str, target_language: str = "İngilizce", model: str = "gpt-3.5-turbo"):
    """
    Hızlı metin çeviri endpoint
    """
    try:
        messages = [
            {"role": "system", "content": f"Sen bir çevirmensin. Verilen metni {target_language} diline çevir."},
            {"role": "user", "content": text}
        ]
        
        response_content = get_openai_response(messages, model, 0.3, 200)
        
        return {
            "original_text": text,
            "target_language": target_language,
            "translation": response_content,
            "model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    404 hatası için custom handler
    """
    return {
        "error": "Endpoint bulunamadı",
        "path": str(request.url.path),
        "available_endpoints": ["/chat", "/text/process", "/code/explain"]
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    500 hatası için custom handler
    """
    return {
        "error": "Internal server error",
        "message": str(exc),
        "path": str(request.url.path)
    }


# ============================================================================
# UYGULAMA ÇALIŞTIRMA
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "3_fastapi_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

