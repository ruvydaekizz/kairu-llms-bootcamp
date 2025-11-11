"""
Docker Setup ve Deployment Script
Docker container'larını yönetmek için yardımcı script
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Environment variables yükle
load_dotenv()

# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def run_command(command, check=True):
    """
    Terminal komutu çalıştır
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Hata: {e}")
        print(f"Stderr: {e.stderr}")
        return None


def check_docker_installed():
    """
    Docker'ın yüklü olup olmadığını kontrol et
    """
    result = run_command("docker --version", check=False)
    if result:
        print(f"✅ Docker yüklü: {result}")
        return True
    else:
        print("❌ Docker yüklü değil!")
        print("Docker'ı yüklemek için: https://docs.docker.com/get-docker/")
        return False


def check_docker_compose_installed():
    """
    Docker Compose'un yüklü olup olmadığını kontrol et
    """
    result = run_command("docker-compose --version", check=False)
    if result:
        print(f"✅ Docker Compose yüklü: {result}")
        return True
    else:
        print("❌ Docker Compose yüklü değil!")
        print("Docker Compose'u yüklemek için: https://docs.docker.com/compose/install/")
        return False


def check_env_file():
    """
    .env dosyasının var olup olmadığını kontrol et
    """
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env dosyası bulundu")
        return True
    else:
        print("⚠️ .env dosyası bulunamadı!")
        print("Lütfen .env dosyası oluşturun:")
        print("  OPENAI_API_KEY=your-api-key")
        print("  HUGGINGFACE_API_KEY=your-api-key")
        return False


def build_backend_image():
    """
    Backend API Docker image'ını build et
    """
    print("\n🔨 Backend API image'ı build ediliyor...")
    result = run_command("docker build -t llm-backend:latest -f Dockerfile .")
    if result is not None:
        print("✅ Backend API image başarıyla build edildi")
        return True
    else:
        print("❌ Backend API image build edilemedi")
        return False


def build_gradio_image():
    """
    Gradio frontend Docker image'ını build et
    """
    print("\n🔨 Gradio frontend image'ı build ediliyor...")
    result = run_command("docker build -t llm-gradio:latest -f Dockerfile.gradio .")
    if result is not None:
        print("✅ Gradio frontend image başarıyla build edildi")
        return True
    else:
        print("❌ Gradio frontend image build edilemedi")
        return False


def build_streamlit_image():
    """
    Streamlit frontend Docker image'ını build et
    """
    print("\n🔨 Streamlit frontend image'ı build ediliyor...")
    result = run_command("docker build -t llm-streamlit:latest -f Dockerfile.streamlit .")
    if result is not None:
        print("✅ Streamlit frontend image başarıyla build edildi")
        return True
    else:
        print("❌ Streamlit frontend image build edilemedi")
        return False


def start_backend_container():
    """
    Backend API container'ını başlat
    """
    print("\n🚀 Backend API container başlatılıyor...")
    
    # Önce durdur (varsa)
    run_command("docker stop llm-backend 2>/dev/null", check=False)
    run_command("docker rm llm-backend 2>/dev/null", check=False)
    
    # Container'ı başlat
    result = run_command(
        "docker run -d "
        "--name llm-backend "
        "-p 8000:8000 "
        "--env-file .env "
        "llm-backend:latest"
    )
    
    if result:
        print("✅ Backend API container başlatıldı")
        print("   URL: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        return True
    else:
        print("❌ Backend API container başlatılamadı")
        return False


def start_gradio_container():
    """
    Gradio frontend container'ını başlat
    """
    print("\n🚀 Gradio frontend container başlatılıyor...")
    
    # Önce durdur (varsa)
    run_command("docker stop llm-gradio-frontend 2>/dev/null", check=False)
    run_command("docker rm llm-gradio-frontend 2>/dev/null", check=False)
    
    # Container'ı başlat
    result = run_command(
        "docker run -d "
        "--name llm-gradio-frontend "
        "-p 7860:7860 "
        "-e API_BASE_URL=http://host.docker.internal:8000 "
        "llm-gradio:latest"
    )
    
    if result:
        print("✅ Gradio frontend container başlatıldı")
        print("   URL: http://localhost:7860")
        return True
    else:
        print("❌ Gradio frontend container başlatılamadı")
        return False


def start_streamlit_container():
    """
    Streamlit frontend container'ını başlat
    """
    print("\n🚀 Streamlit frontend container başlatılıyor...")
    
    # Önce durdur (varsa)
    run_command("docker stop llm-streamlit-frontend 2>/dev/null", check=False)
    run_command("docker rm llm-streamlit-frontend 2>/dev/null", check=False)
    
    # Container'ı başlat
    result = run_command(
        "docker run -d "
        "--name llm-streamlit-frontend "
        "-p 8501:8501 "
        "-e API_BASE_URL=http://host.docker.internal:8000 "
        "llm-streamlit:latest"
    )
    
    if result:
        print("✅ Streamlit frontend container başlatıldı")
        print("   URL: http://localhost:8501")
        return True
    else:
        print("❌ Streamlit frontend container başlatılamadı")
        return False


def start_with_compose():
    """
    Docker Compose ile tüm servisleri başlat
    """
    print("\n🚀 Docker Compose ile servisler başlatılıyor...")
    result = run_command("docker-compose up -d")
    
    if result is not None:
        print("✅ Tüm servisler başlatıldı")
        print("\n📊 Servisler:")
        print("   Backend API: http://localhost:8000")
        print("   Backend Docs: http://localhost:8000/docs")
        print("   Gradio Frontend: http://localhost:7860")
        print("   Streamlit Frontend: http://localhost:8501")
        return True
    else:
        print("❌ Servisler başlatılamadı")
        return False


def stop_containers():
    """
    Tüm container'ları durdur
    """
    print("\n🛑 Container'lar durduruluyor...")
    run_command("docker-compose down", check=False)
    run_command("docker stop llm-backend llm-gradio-frontend llm-streamlit-frontend 2>/dev/null", check=False)
    print("✅ Container'lar durduruldu")


def show_logs(service=None):
    """
    Container loglarını göster
    """
    if service:
        print(f"\n📋 {service} logları:")
        run_command(f"docker logs -f {service}", check=False)
    else:
        print("\n📋 Tüm loglar:")
        run_command("docker-compose logs -f", check=False)


def show_status():
    """
    Container durumlarını göster
    """
    print("\n📊 Container Durumları:")
    run_command("docker ps -a --filter name=llm-", check=False)


# ============================================================================
# ANA MENÜ
# ============================================================================

def main():
    """
    Ana menü
    """
    print("=" * 60)
    print("🐳 Docker Setup ve Deployment Script")
    print("=" * 60)
    
    # Kontroller
    if not check_docker_installed():
        sys.exit(1)
    
    check_docker_compose_installed()
    check_env_file()
    
    print("\n" + "=" * 60)
    print("Menü:")
    print("1. Backend API image build et")
    print("2. Gradio frontend image build et")
    print("3. Streamlit frontend image build et")
    print("4. Tüm image'ları build et")
    print("5. Backend API container başlat")
    print("6. Gradio frontend container başlat")
    print("7. Streamlit frontend container başlat")
    print("8. Docker Compose ile tüm servisleri başlat")
    print("9. Container'ları durdur")
    print("10. Container durumlarını göster")
    print("11. Logları göster")
    print("0. Çıkış")
    print("=" * 60)
    
    choice = input("\nSeçiminiz (0-11): ").strip()
    
    if choice == "1":
        build_backend_image()
    elif choice == "2":
        build_gradio_image()
    elif choice == "3":
        build_streamlit_image()
    elif choice == "4":
        build_backend_image()
        build_gradio_image()
        build_streamlit_image()
    elif choice == "5":
        start_backend_container()
    elif choice == "6":
        start_gradio_container()
    elif choice == "7":
        start_streamlit_container()
    elif choice == "8":
        start_with_compose()
    elif choice == "9":
        stop_containers()
    elif choice == "10":
        show_status()
    elif choice == "11":
        service = input("Service adı (boş bırakınca tümü): ").strip()
        show_logs(service if service else None)
    elif choice == "0":
        print("Çıkılıyor...")
        sys.exit(0)
    else:
        print("❌ Geçersiz seçim!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ İşlem iptal edildi.")
        sys.exit(0)

