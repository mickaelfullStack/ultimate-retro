#!/usr/bin/env python3
import os
import requests
from pathlib import Path
import time

# Configurações atualizadas
CONFIG_FILE = "games_data.txt"
COVERS_DIR = "covers"
GAMES_DIR = "games"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TIMEOUT = 30
CHUNK_SIZE = 8192
MAX_RETRIES = 2  # Reduzido para testes
DELAY_BETWEEN_DOWNLOADS = 3

def setup_environment():
    """Configura os diretórios necessários"""
    try:
        Path(COVERS_DIR).mkdir(parents=True, exist_ok=True)
        for platform in ["ps1", "ps2", "psp", "ps3", "nintendo", "sega", "xbox"]:
            Path(os.path.join(GAMES_DIR, platform)).mkdir(parents=True, exist_ok=True)
        print("✅ Estrutura de diretórios configurada")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar ambiente: {e}")
        return False

def load_game_data():
    """Carrega os dados dos jogos do arquivo de configuração"""
    games = []
    try:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(';')
                    if len(parts) >= 3:
                        game = {
                            "name": parts[0].strip(),
                            "cover_url": parts[1].strip(),
                            "download_url": parts[2].strip(),
                            "platform": "ps2"  # Default
                        }
                        
                        # Determina a plataforma
                        if "_PS1" in game["name"]: game["platform"] = "ps1"
                        elif "_PSP" in game["name"]: game["platform"] = "psp"
                        elif "_PS3" in game["name"]: game["platform"] = "ps3"
                        elif "_Nintendo" in game["name"]: game["platform"] = "nintendo"
                        elif "_Sega" in game["name"]: game["platform"] = "sega"
                        elif "_Xbox" in game["name"]: game["platform"] = "xbox"
                            
                        game["cover_path"] = os.path.join(COVERS_DIR, f"{game['name']}.jpg")
                        game["game_path"] = os.path.join(GAMES_DIR, game["platform"], f"{game['name']}.iso")
                        games.append(game)
        return games
    except Exception as e:
        print(f"❌ Erro ao ler arquivo de configuração: {e}")
        return []

def download_file(url, filepath, file_type="game"):
    """Baixa um arquivo com tratamento de erros robusto"""
    if not url.startswith('http'):
        print(f"⚠️ URL inválida para {file_type}: {url}")
        return False

    temp_path = f"{filepath}.temp"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        # Verifica se o arquivo final já existe
        if os.path.exists(filepath):
            print(f"✔️ {file_type.capitalize()} já existe: {os.path.basename(filepath)}")
            return True

        print(f"⬇️ Baixando {file_type}...")
        with requests.get(url, headers=headers, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(temp_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        print(f"📊 Progresso: {downloaded/1024/1024:.2f}MB", end='\r')
            
            # Verifica se o download está completo
            if total_size > 0 and downloaded != total_size:
                raise Exception(f"Download incompleto (esperado: {total_size}, baixado: {downloaded})")
            
            # Renomeia o arquivo temporário
            os.rename(temp_path, filepath)
            print(f"\n✅ {file_type.capitalize()} baixado com sucesso!")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro ao baixar {file_type}: {e}")
        # Remove arquivos temporários em caso de erro
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def download_game_assets(game):
    """Gerencia o download de todos os assets de um jogo"""
    print(f"\n{'='*60}")
    print(f"🎮 Processando: {game['name']} ({game['platform'].upper()})")
    
    # Baixa a capa (se URL for válida)
    cover_success = True
    if game['cover_url'].startswith('http'):
        cover_success = download_file(game['cover_url'], game['cover_path'], "capa")
    
    # Baixa o jogo principal
    game_success = True
    if game['download_url'].startswith('http'):
        game_success = download_file(game['download_url'], game['game_path'], "jogo")
    
    return cover_success and game_success

def main():
    print("""
    ============================================
    ULTIMATE RETRO GAME DOWNLOADER (ATUALIZADO)
    ============================================
    Sistema seguro de download sequencial de ISOs
    Verifique as leis de copyright do seu país!
    ============================================
    """)
    
    if not setup_environment():
        return
    
    games = load_game_data()
    if not games:
        print(f"❌ Nenhum jogo encontrado em {CONFIG_FILE}")
        print(f"Edite o arquivo com o formato: Nome;URL_Capa;URL_Download")
        return
    
    print(f"\n🎮 {len(games)} jogos encontrados para processar")
    
    success_count = 0
    for i, game in enumerate(games, 1):
        print(f"\n🔷 Progresso: {i}/{len(games)}")
        
        if download_game_assets(game):
            success_count += 1
        
        # Intervalo entre jogos (exceto após o último)
        if i < len(games):
            print(f"\n⏳ Aguardando {DELAY_BETWEEN_DOWNLOADS} segundos...")
            time.sleep(DELAY_BETWEEN_DOWNLOADS)
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL:")
    print(f"- Total de jogos: {len(games)}")
    print(f"- Processados com sucesso: {success_count}")
    print(f"- Falhas: {len(games) - success_count}")
    print(f"\n💾 Jogos salvos em: {os.path.abspath(GAMES_DIR)}")
    print(f"🖼️ Capas salvas em: {os.path.abspath(COVERS_DIR)}")
    print("="*60)

if __name__ == "__main__":
    main()