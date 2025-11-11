#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"API anahtarı bulundu: {api_key[:10]}...")
else:
    print("API anahtarı bulunamadı!")