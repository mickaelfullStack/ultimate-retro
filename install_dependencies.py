import os
import sys
import subprocess
import platform
from pathlib import Path

def install_python_dependencies():
    """Instala todas as dependências Python necessárias"""
    print("🛠 Instalando dependências Python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências Python instaladas com sucesso!")
    except subprocess.CalledProcessError:
        print("❌ Falha ao instalar dependências Python")
        sys.exit(1)

def install_system_dependencies():
    """Instala dependências específicas do sistema"""
    system = platform.system()
    print(f"🖥 Detectado sistema: {system}")
    
    if system == "Linux":
        print("📦 Instalando dependências do sistema para Linux...")
        try:
            # Instala o 7z se necessário
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "p7zip-full", "libsdl2-2.0-0", "libgl1"], check=True)
            print("✅ Dependências do Linux instaladas com sucesso!")
        except subprocess.CalledProcessError:
            print("⚠️ Não foi possível instalar todas as dependências do sistema")
    
    elif system == "Windows":
        print("ℹ️ No Windows, certifique-se de ter o 7-Zip instalado")
        print("📥 Baixe em: https://www.7-zip.org/download.html")

def create_directories():
    """Cria a estrutura de diretórios necessária"""
    print("📂 Criando estrutura de diretórios...")
    directories = [
        "emuladores",
        "bios",
        "games",
        "fonts",
        "logos",
        "thumbs",
        "background"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✔️ Diretório {directory}/ criado")
    
    # Subdiretórios específicos
    (Path("emuladores") / "ps2").mkdir(exist_ok=True)
    (Path("bios") / "ps2").mkdir(exist_ok=True)
    (Path("games") / "ps2").mkdir(exist_ok=True)

def main():
    print("\n" + "="*50)
    print("🛠 INSTALADOR ULTIMATE RETRO EMULATOR")
    print("="*50 + "\n")
    
    # Verifica a versão do Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário")
        sys.exit(1)
    
    # Instala dependências
    install_python_dependencies()
    install_system_dependencies()
    create_directories()
    
    print("\n" + "="*50)
    print("✅ Instalação concluída com sucesso!")
    print("👉 Execute o emulador com: python main.py")
    print("="*50)

if __name__ == "__main__":
    main()