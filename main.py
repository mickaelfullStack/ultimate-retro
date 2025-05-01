import os
import sys
import pygame
from pygame.locals import *
import subprocess
import requests
import shutil
import zipfile
import io
import platform
import webbrowser
from pathlib import Path

# Initialization
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Ultimate Retro Emulator")

# Settings
clock = pygame.time.Clock()
FPS = 60
fullscreen = False
VERSION = "1.0.0"

# Colors
BACKGROUND = (15, 15, 20)
MENU_BG = (25, 25, 30)
WHITE = (240, 240, 240)
ACCENT_COLOR = (50, 150, 255)
HIGHLIGHT_COLOR = (255, 200, 0)
TEXT_COLOR = (180, 180, 180)

# Fonts (relative sizes)
def get_scaled_font_sizes(base_size):
    return {
        "title": int(base_size * 0.05),
        "platform": int(base_size * 0.03),
        "menu": int(base_size * 0.025),
        "game": int(base_size * 0.02),
        "info": int(base_size * 0.018)
    }

# Available platforms
PLATFORMS = [
    {"name": "PS1", "logo": "ps1.webp", "color": (0, 70, 140), "thumbnail": "thumb_ps1.png"},
    {"name": "PS2", "logo": "ps2.png", "color": (0, 100, 180), "thumbnail": "Thumbnail-ps2.png"},
    {"name": "PSP", "logo": "psp.svg", "color": (0, 130, 200), "thumbnail": "Thumbnail-psp.png"},
    {"name": "PS3", "logo": "ps3.svg", "color": (0, 160, 220), "thumbnail": "Thumbnail-ps3.png"},
    {"name": "PS4", "logo": "ps4.png", "color": (0, 100, 200), "thumbnail": "Thumbnail-ps4.png"},
    {"name": "PS5", "logo": "ps5.png", "color": (0, 150, 255), "thumbnail": "Thumbnail-ps5.png"},
    {"name": "Nintendo", "logo": "nintendo.png", "color": (220, 0, 0), "thumbnail": "Thumbnail-nintendo.png"},
    {"name": "Sega", "logo": "sega.png", "color": (150, 0, 220), "thumbnail": "Thumbnail-sega.png"},
    {"name": "Xbox", "logo": "xbox.png", "color": (0, 180, 0), "thumbnail": "Thumbnail-xbox.png"}
]

class EmulatorManager:
    EMULATORS_DIR = "emuladores"
    BIOS_DIR = "bios"
    GAMES_DIR = "games"
    
    @staticmethod
    def get_platform_specific_pcsx2():
        system = platform.system()
        if system == "Windows":
            return {
                "name": "PCSX2",
                "executable": "pcsx2.exe",
                "download_url": "https://github.com/PCSX2/pcsx2/releases/download/v1.7.0/pcsx2-v1.7.0-windows-64bit-AVX2-Qt.7z",
                "bios_required": True
            }
        elif system == "Linux":
            return {
                "name": "PCSX2",
                "executable": "pcsx2-qt",
                "install_command": "sudo apt-get install pcsx2",
                "bios_required": True
            }
        elif system == "Darwin":  # macOS
            return {
                "name": "PCSX2",
                "executable": "PCSX2",
                "download_url": "https://github.com/PCSX2/pcsx2/releases/download/v1.7.0/pcsx2-v1.7.0-macOS-Qt.tar.xz",
                "bios_required": True
            }
        else:
            return None
    
    @staticmethod
    def ensure_directories_exist():
        Path(EmulatorManager.EMULATORS_DIR).mkdir(exist_ok=True)
        Path(EmulatorManager.BIOS_DIR).mkdir(exist_ok=True)
        Path(EmulatorManager.GAMES_DIR).mkdir(exist_ok=True)
    
    @staticmethod
    def download_file(url, destination):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Erro ao baixar arquivo: {e}")
            return False
    
    @staticmethod
    def extract_archive(archive_path, destination):
        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(destination)
            elif archive_path.endswith('.7z'):
                # Requer o 7z instalado no sistema
                subprocess.run(["7z", "x", archive_path, f"-o{destination}"], check=True)
            elif archive_path.endswith('.tar.xz'):
                subprocess.run(["tar", "-xf", archive_path, "-C", destination], check=True)
            return True
        except Exception as e:
            print(f"Erro ao extrair arquivo: {e}")
            return False
    
    @staticmethod
    def install_pcsx2():
        EmulatorManager.ensure_directories_exist()
        pcsx2_info = EmulatorManager.get_platform_specific_pcsx2()
        
        if not pcsx2_info:
            print("Sistema operacional não suportado para PCSX2")
            return False
        
        ps2_dir = Path(EmulatorManager.EMULATORS_DIR) / "ps2"
        ps2_dir.mkdir(exist_ok=True)
        
        # Verifica se já está instalado
        executable_path = ps2_dir / pcsx2_info["executable"]
        if executable_path.exists():
            return True
        
        # Se for Linux e tiver comando de instalação
        if "install_command" in pcsx2_info:
            try:
                subprocess.run(pcsx2_info["install_command"].split(), check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        
        # Para Windows e macOS, baixa e extrai
        if "download_url" in pcsx2_info:
            archive_name = pcsx2_info["download_url"].split('/')[-1]
            archive_path = ps2_dir / archive_name
            
            # Mostrar mensagem de progresso
            print(f"Baixando PCSX2 de {pcsx2_info['download_url']}...")
            
            if EmulatorManager.download_file(pcsx2_info["download_url"], archive_path):
                print("Extraindo PCSX2...")
                if EmulatorManager.extract_archive(archive_path, ps2_dir):
                    archive_path.unlink()  # Remove o arquivo após extrair
                    print("PCSX2 instalado com sucesso!")
                    return True
        
        return False
    
    @staticmethod
    def download_game(url, game_name):
        EmulatorManager.ensure_directories_exist()
        game_path = Path(EmulatorManager.GAMES_DIR) / "ps2" / f"{game_name}.iso"
        game_path.parent.mkdir(exist_ok=True)
        
        if game_path.exists():
            return game_path
        
        print(f"Baixando jogo {game_name}...")
        if EmulatorManager.download_file(url, game_path):
            print("Jogo baixado com sucesso!")
            return game_path
        return None
    
    @staticmethod
    def run_pcsx2(game_path=None, fullscreen=False):
        pcsx2_info = EmulatorManager.get_platform_specific_pcsx2()
        if not pcsx2_info:
            return False
        
        ps2_dir = Path(EmulatorManager.EMULATORS_DIR) / "ps2"
        executable_path = ps2_dir / pcsx2_info["executable"]
        
        if not executable_path.exists():
            if not EmulatorManager.install_pcsx2():
                return False
        
        bios_path = Path(EmulatorManager.BIOS_DIR) / "ps2"
        if pcsx2_info["bios_required"] and not any(bios_path.glob("*")):
            print("BIOS do PS2 não encontrada. Por favor, coloque os arquivos BIOS em emuladores/bios/ps2/")
            webbrowser.open("https://pcsx2.net/getting-started.html")
            return False
        
        try:
            args = [str(executable_path)]
            if game_path:
                args.extend(["--nogui", "--fullscreen" if fullscreen else "--windowed", str(game_path)])
            
            print(f"Executando PCSX2 com args: {args}")
            subprocess.Popen(args, cwd=ps2_dir)
            return True
        except Exception as e:
            print(f"Erro ao executar PCSX2: {e}")
            return False

class AssetManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.background = None
        self.base_size = min(WIDTH, HEIGHT)
        self.font_sizes = get_scaled_font_sizes(self.base_size)
        self.margin = int(self.base_size * 0.02)
        self.button_height = int(self.base_size * 0.06)
        self.load_fonts()
        self.load_background()

    def load_fonts(self):
        try:
            self.fonts = {
                "title": pygame.font.Font("fonts/retro.otf", self.font_sizes["title"]),
                "platform": pygame.font.Font("fonts/retro.otf", self.font_sizes["platform"]),
                "menu": pygame.font.Font("fonts/retro.otf", self.font_sizes["menu"]),
                "game": pygame.font.Font("fonts/retro.otf", self.font_sizes["game"]),
                "info": pygame.font.Font("fonts/retro.otf", self.font_sizes["info"])
            }
        except:
            self.fonts = {
                "title": pygame.font.SysFont("arial", self.font_sizes["title"], bold=True),
                "platform": pygame.font.SysFont("arial", self.font_sizes["platform"], bold=True),
                "menu": pygame.font.SysFont("arial", self.font_sizes["menu"]),
                "game": pygame.font.SysFont("arial", self.font_sizes["game"]),
                "info": pygame.font.SysFont("arial", self.font_sizes["info"])
            }

    def load_background(self):
        try:
            bg = pygame.image.load("background/background.webp")
            bg_ratio = bg.get_width() / bg.get_height()
            screen_ratio = WIDTH / HEIGHT
            
            if bg_ratio > screen_ratio:
                new_height = HEIGHT
                new_width = int(new_height * bg_ratio)
            else:
                new_width = WIDTH
                new_height = int(new_width / bg_ratio)
                
            self.background = pygame.transform.scale(bg, (new_width, new_height))
        except:
            self.background = pygame.Surface((WIDTH, HEIGHT))
            self.background.fill(BACKGROUND)

    def get_image(self, path, size=None):
        key = f"{path}_{size[0]}_{size[1]}" if size else path
        if key not in self.images:
            try:
                image = pygame.image.load(path)
                if size:
                    img_ratio = image.get_width() / image.get_height()
                    target_ratio = size[0] / size[1]
                    
                    if img_ratio > target_ratio:
                        new_width = size[0]
                        new_height = int(new_width / img_ratio)
                    else:
                        new_height = size[1]
                        new_width = int(new_height * img_ratio)
                        
                    image = pygame.transform.scale(image, (new_width, new_height))
                    surf = pygame.Surface(size, pygame.SRCALPHA)
                    x = (size[0] - new_width) // 2
                    y = (size[1] - new_height) // 2
                    surf.blit(image, (x, y))
                    self.images[key] = surf
                else:
                    self.images[key] = image
            except:
                size = size or (100, 100)
                surf = pygame.Surface(size)
                surf.fill(MENU_BG)
                text = self.fonts["info"].render("IMG", True, WHITE)
                text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
                surf.blit(text, text_rect)
                self.images[key] = surf
        return self.images[key]

    def update_sizes(self, width, height):
        self.base_size = min(width, height)
        self.font_sizes = get_scaled_font_sizes(self.base_size)
        self.margin = int(self.base_size * 0.02)
        self.button_height = int(self.base_size * 0.06)
        self.load_fonts()
        self.load_background()

class Carousel:
    def __init__(self, platforms, y_pos, assets):
        self.platforms = platforms
        self.selected = 0
        self.x_start = 0
        self.y_pos = y_pos
        self.assets = assets
        self.visible = True
        self.elevation = 0
        self.max_elevation = 20
        self.animating = False
        self.animation_speed = 2
        self.scroll_offset = 0
        self.scroll_speed = 15
        self.target_offset = 0
        
        self.logo_size = int(self.assets.base_size * 0.12)
        self.item_width = self.logo_size * 1.8
        self.spacing = int(self.assets.base_size * 0.03)
        self.item_height = self.logo_size + 40
        
        for platform in self.platforms:
            platform["image"] = self.assets.get_image(
                f"logos/{platform['logo']}", 
                (self.logo_size, self.logo_size)
            )
        
    def move_selection(self, direction):
        prev_selected = self.selected
        
        if direction == "left":
            self.selected = max(0, self.selected - 1)
        elif direction == "right":
            self.selected = min(len(self.platforms) - 1, self.selected + 1)
        
        if prev_selected != self.selected:
            self.animating = True
            self.elevation = 0
            self.adjust_scroll()
            return True  # Indicates selection changed
        return False
            
    def adjust_scroll(self):
        total_width = len(self.platforms) * (self.item_width + self.spacing)
        visible_width = WIDTH
        
        if total_width <= visible_width:
            self.target_offset = (visible_width - total_width) // 2
            return
            
        item_center = self.selected * (self.item_width + self.spacing) + (self.item_width // 2)
        target_offset = (visible_width // 2) - item_center
        
        max_offset = 20
        min_offset = visible_width - total_width - 20
        
        if target_offset > max_offset:
            self.target_offset = max_offset + (target_offset - max_offset) * 0.3
        elif target_offset < min_offset:
            self.target_offset = min_offset + (target_offset - min_offset) * 0.3
        else:
            self.target_offset = target_offset
            
    def update(self):
        if self.animating:
            if self.elevation < self.max_elevation:
                self.elevation += self.animation_speed
            else:
                self.animating = False
                
        if abs(self.scroll_offset - self.target_offset) > 1:
            diff = self.target_offset - self.scroll_offset
            self.scroll_offset += diff * 0.2
        else:
            self.scroll_offset = self.target_offset
                
    def draw(self, surface):
        if not self.visible:
            return
            
        total_width = len(self.platforms) * (self.item_width + self.spacing)
        self.x_start = (WIDTH - total_width) // 2 + self.scroll_offset
        
        for i, platform in enumerate(self.platforms):
            x = self.x_start + i * (self.item_width + self.spacing)
            
            if x + self.item_width < 0 or x > WIDTH:
                continue
                
            y_offset = -self.elevation if i == self.selected else 0
            
            if i == self.selected:
                shadow = pygame.Surface((self.item_width + 20, self.item_height + 20), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 100))
                shadow_rect = shadow.get_rect(center=(
                    x + self.item_width//2, 
                    self.y_pos + self.item_height//2 + y_offset + 5
                ))
                surface.blit(shadow, shadow_rect)
                
                pygame.draw.rect(surface, platform["color"], 
                               (x - 10, self.y_pos - 10 + y_offset, 
                                self.item_width + 20, self.item_height + 20),
                               border_radius=10)
            
            logo_rect = platform["image"].get_rect(center=(
                x + self.item_width//2, 
                self.y_pos + self.logo_size//2 + y_offset
            ))
            surface.blit(platform["image"], logo_rect)
            
            name = self.assets.fonts["platform"].render(platform["name"], True, WHITE)
            name_rect = name.get_rect(center=(
                x + self.item_width//2, 
                self.y_pos + self.logo_size + 25 + y_offset
            ))
            surface.blit(name, name_rect)

class GameSelection:
    def __init__(self, platform, assets):
        self.platform = platform
        self.assets = assets
        self.games = self.load_games()
        self.selected = 0
        self.visible = False
        self.columns = max(2, WIDTH // (int(WIDTH * 0.25) + self.assets.margin))
        self.elevations = [0] * len(self.games)
        self.max_elevation = 15
        self.animation_speed = 2
        
        self.game_width = int(WIDTH * 0.25)
        self.game_height = int(HEIGHT * 0.25)
        
    def load_games(self):
        games = []
        for i in range(1, 10):
            games.append({
                "title": f"Jogo {i} {self.platform['name']}",
                "image": f"games/{self.platform['name'].lower()}/game{i}.png",
                "path": f"games/{self.platform['name'].lower()}/game{i}.iso"
            })
        return games
        
    def move_selection(self, direction):
        prev_selected = self.selected
        
        if direction == "up":
            self.selected = max(0, self.selected - self.columns)
        elif direction == "down":
            self.selected = min(len(self.games) - 1, self.selected + self.columns)
        elif direction == "left":
            if self.selected % self.columns > 0:
                self.selected -= 1
        elif direction == "right":
            if self.selected % self.columns < self.columns - 1 and self.selected < len(self.games) - 1:
                self.selected += 1
                
        self.elevations[prev_selected] = 0
        
    def update(self):
        if self.elevations[self.selected] < self.max_elevation:
            self.elevations[self.selected] += self.animation_speed
                
    def draw(self, surface):
        if not self.visible:
            return
            
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        header_height = self.assets.button_height + self.assets.margin * 2
        header = pygame.Rect(0, 0, WIDTH, header_height)
        pygame.draw.rect(surface, self.platform["color"], header)
        
        title = self.assets.fonts["title"].render(self.platform["name"], True, WHITE)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, self.assets.margin))
        
        back_rect = pygame.Rect(
            self.assets.margin, 
            self.assets.margin, 
            int(WIDTH * 0.15), 
            self.assets.button_height
        )
        pygame.draw.rect(surface, MENU_BG, back_rect, border_radius=5)
        back_text = self.assets.fonts["menu"].render("Voltar", True, WHITE)
        surface.blit(back_text, (
            back_rect.x + (back_rect.width - back_text.get_width()) // 2,
            back_rect.y + (back_rect.height - back_text.get_height()) // 2
        ))
        
        start_x = (WIDTH - (self.columns * self.game_width + (self.columns - 1) * self.assets.margin)) // 2
        start_y = header_height + self.assets.margin * 2
        
        for i, game in enumerate(self.games):
            col = i % self.columns
            row = i // self.columns
            
            x = start_x + col * (self.game_width + self.assets.margin)
            y = start_y + row * (self.game_height + self.assets.margin)
            
            y_offset = -self.elevations[i]
            
            if i == self.selected:
                shadow = pygame.Surface((self.game_width + 10, self.game_height + 10), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 100))
                shadow_rect = shadow.get_rect(center=(
                    x + self.game_width//2, 
                    y + self.game_height//2 + y_offset + 5
                ))
                surface.blit(shadow, shadow_rect)
                
                pygame.draw.rect(surface, HIGHLIGHT_COLOR, (
                    x - 5, y - 5 + y_offset, 
                    self.game_width + 10, self.game_height + 10
                ), border_radius=8)
            
            game_rect = pygame.Rect(x, y + y_offset, self.game_width, self.game_height)
            pygame.draw.rect(surface, MENU_BG, game_rect, border_radius=6)
            
            img = self.assets.get_image(
                game["image"], 
                (self.game_width - 20, self.game_height - 50)
            )
            surface.blit(img, (x + 10, y + 10 + y_offset))
            
            title = self.assets.fonts["game"].render(
                game["title"][:20] + ("..." if len(game["title"]) > 20 else ""), 
                True, WHITE
            )
            surface.blit(title, (x + 10, y + self.game_height - 30 + y_offset))

class SettingsMenu:
    def __init__(self, assets):
        self.assets = assets
        self.visible = False
        self.options = [
            {"text": "Tela Cheia: ON" if fullscreen else "Tela Cheia: OFF", "action": "toggle_fullscreen"},
            {"text": f"Versão: {VERSION}", "action": None},
            {"text": "Sair", "action": "quit"}
        ]
        self.selected = 0
        
    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.selected = 0
        
    def draw(self, surface):
        if not self.visible:
            return
            
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        menu_width = int(WIDTH * 0.15) * 1.5
        menu_height = len(self.options) * self.assets.button_height + self.assets.margin * (len(self.options) + 1)
        menu_rect = pygame.Rect(
            WIDTH//2 - menu_width//2,
            HEIGHT//2 - menu_height//2,
            menu_width,
            menu_height
        )
        pygame.draw.rect(surface, MENU_BG, menu_rect, border_radius=10)
        
        title = self.assets.fonts["title"].render("Configurações", True, WHITE)
        surface.blit(title, (
            WIDTH//2 - title.get_width()//2,
            menu_rect.y + self.assets.margin
        ))
        
        for i, option in enumerate(self.options):
            y_pos = menu_rect.y + self.assets.margin * 2 + self.assets.button_height * i + self.assets.margin * i
            
            if i == self.selected:
                pygame.draw.rect(surface, ACCENT_COLOR, (
                    menu_rect.x + self.assets.margin,
                    y_pos,
                    menu_width - self.assets.margin * 2,
                    self.assets.button_height
                ), border_radius=5)
            
            option_rect = pygame.Rect(
                menu_rect.x + self.assets.margin,
                y_pos,
                menu_width - self.assets.margin * 2,
                self.assets.button_height
            )
            pygame.draw.rect(surface, (40, 40, 50), option_rect, border_radius=5)
            
            text = self.assets.fonts["menu"].render(option["text"], True, WHITE)
            surface.blit(text, (
                option_rect.x + (option_rect.width - text.get_width()) // 2,
                option_rect.y + (option_rect.height - text.get_height()) // 2
            ))
    
    def handle_input(self, event):
        if not self.visible:
            return False
            
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.selected = max(0, self.selected - 1)
            elif event.key == K_DOWN:
                self.selected = min(len(self.options) - 1, self.selected + 1)
            elif event.key == K_RETURN:
                action = self.options[self.selected]["action"]
                if action == "toggle_fullscreen":
                    return "toggle_fullscreen"
                elif action == "quit":
                    return "quit"
            elif event.key == K_ESCAPE:
                self.visible = False
                
        return None

class Emulator:
    def __init__(self):
        self.assets = AssetManager()
        self.carousel = Carousel(PLATFORMS, HEIGHT - int(self.assets.base_size * 0.3), self.assets)
        self.game_selection = None
        self.settings = SettingsMenu(self.assets)
        self.running = True
        self.current_screen = "platforms"
        self.thumbnail = None
        self.last_selected = -1  # Track last selected platform
        self.emulator_manager = EmulatorManager()
        
        # Verificar instalação do emulador PS2
        self.check_emulator_installation()
    
    def check_emulator_installation(self):
        # Verifica se o emulador PS2 está instalado
        ps2_platform = next((p for p in PLATFORMS if p["name"] == "PS2"), None)
        if ps2_platform:
            if not self.emulator_manager.install_pcsx2():
                ps2_platform["name"] = "PS2 (Instalar)"
                ps2_platform["color"] = (255, 50, 50)  # Vermelho para indicar problema
    
    def toggle_fullscreen(self):
        global fullscreen, screen, WIDTH, HEIGHT
        fullscreen = not fullscreen
        if fullscreen:
            screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            self.settings.options[0]["text"] = "Tela Cheia: ON"
        else:
            screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
            self.settings.options[0]["text"] = "Tela Cheia: OFF"
        self.update_sizes()
        
    def update_sizes(self):
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = screen.get_width(), screen.get_height()
        self.assets.update_sizes(WIDTH, HEIGHT)
        self.carousel = Carousel(PLATFORMS, HEIGHT - int(self.assets.base_size * 0.3), self.assets)
        self.settings = SettingsMenu(self.assets)
        if self.current_screen == "games":
            selected_platform = PLATFORMS[self.carousel.selected]
            self.game_selection = GameSelection(selected_platform, self.assets)
            self.game_selection.visible = True
        self.update_thumbnail()  # Update thumbnail when resizing
        
    def update_thumbnail(self):
        selected_platform = PLATFORMS[self.carousel.selected]
        try:
            self.thumbnail = self.assets.get_image(
                f"thumbs/{selected_platform['thumbnail']}", 
                (int(WIDTH * 0.6), int(HEIGHT * 0.4))
            )
        except:
            # Fallback if thumbnail doesn't exist
            self.thumbnail = pygame.Surface((int(WIDTH * 0.6), int(HEIGHT * 0.4)))
            self.thumbnail.fill(selected_platform["color"])
            text = self.assets.fonts["title"].render(selected_platform["name"], True, WHITE)
            text_rect = text.get_rect(center=(self.thumbnail.get_width()//2, self.thumbnail.get_height()//2))
            self.thumbnail.blit(text, text_rect)
        
    def launch_game(self, game):
        print(f"Iniciando jogo: {game['title']}")
        
        # Verifica se é um jogo de PS2
        if "PS2" in game["title"]:
            if "Instalar" in next((p["name"] for p in PLATFORMS if p["name"] == "PS2 (Instalar)"), ""):
                # Se o emulador precisa ser instalado
                if self.emulator_manager.install_pcsx2():
                    # Atualiza a UI após instalação bem-sucedida
                    ps2_platform = next(p for p in PLATFORMS if p["name"] == "PS2 (Instalar)")
                    ps2_platform["name"] = "PS2"
                    ps2_platform["color"] = (0, 100, 180)
                    self.carousel.platforms = PLATFORMS  # Atualiza a lista no carrossel
                else:
                    print("Falha ao instalar o PCSX2")
                    return
            
            # URL do jogo específico que você mencionou
            game_url = "https://firebasestorage.googleapis.com/v0/b/nerdflix-111cc.appspot.com/o/games%2Fchino-pes2014.iso?alt=media&token=64410bf6-dc2d-46b0-ab1b-7d50bff08151"
            
            # Mostrar mensagem de carregamento
            loading_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            loading_surface.fill((0, 0, 0, 200))
            loading_text = self.assets.fonts["title"].render("Baixando jogo...", True, WHITE)
            loading_surface.blit(loading_text, (
                WIDTH//2 - loading_text.get_width()//2,
                HEIGHT//2 - loading_text.get_height()//2
            ))
            screen.blit(loading_surface, (0, 0))
            pygame.display.flip()
            
            # Baixar o jogo
            game_path = self.emulator_manager.download_game(game_url, "pes2014")
            
            if game_path:
                # Executar o emulador
                success = self.emulator_manager.run_pcsx2(game_path, fullscreen)
                if not success:
                    error_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    error_surface.fill((0, 0, 0, 200))
                    error_text = self.assets.fonts["title"].render("Erro ao iniciar PCSX2", True, (255, 50, 50))
                    error_surface.blit(error_text, (
                        WIDTH//2 - error_text.get_width()//2,
                        HEIGHT//2 - error_text.get_height()//2
                    ))
                    screen.blit(error_surface, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)  # Mostra o erro por 2 segundos
            else:
                error_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                error_surface.fill((0, 0, 0, 200))
                error_text = self.assets.fonts["title"].render("Erro ao baixar o jogo", True, (255, 50, 50))
                error_surface.blit(error_text, (
                    WIDTH//2 - error_text.get_width()//2,
                    HEIGHT//2 - error_text.get_height()//2
                ))
                screen.blit(error_surface, (0, 0))
                pygame.display.flip()
                pygame.time.delay(2000)  # Mostra o erro por 2 segundos
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.settings.visible:
                        self.settings.visible = False
                    elif self.current_screen == "games":
                        self.current_screen = "platforms"
                        self.game_selection.visible = False
                        self.carousel.visible = True
                    else:
                        self.running = False
                
                if not self.settings.visible:
                    if self.current_screen == "platforms":
                        selection_changed = False
                        if event.key == K_LEFT:
                            selection_changed = self.carousel.move_selection("left")
                        elif event.key == K_RIGHT:
                            selection_changed = self.carousel.move_selection("right")
                        elif event.key == K_RETURN:
                            self.current_screen = "games"
                            self.carousel.visible = False
                            selected_platform = PLATFORMS[self.carousel.selected]
                            self.game_selection = GameSelection(selected_platform, self.assets)
                            self.game_selection.visible = True
                        elif event.key == K_c:
                            self.settings.toggle()
                        
                        if selection_changed:
                            self.update_thumbnail()
                    
                    elif self.current_screen == "games":
                        if event.key == K_UP:
                            self.game_selection.move_selection("up")
                        elif event.key == K_DOWN:
                            self.game_selection.move_selection("down")
                        elif event.key == K_LEFT:
                            self.game_selection.move_selection("left")
                        elif event.key == K_RIGHT:
                            self.game_selection.move_selection("right")
                        elif event.key == K_RETURN:
                            self.launch_game(self.game_selection.games[self.game_selection.selected])
            
            if self.settings.visible:
                result = self.settings.handle_input(event)
                if result == "toggle_fullscreen":
                    self.toggle_fullscreen()
                elif result == "quit":
                    self.running = False
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.current_screen == "games":
                    button_width = int(WIDTH * 0.15)
                    button_height = self.assets.button_height
                    margin = self.assets.margin
                    
                    if (margin <= mouse_pos[0] <= margin + button_width and 
                        margin <= mouse_pos[1] <= margin + button_height):
                        self.current_screen = "platforms"
                        self.game_selection.visible = False
                        self.carousel.visible = True
    
    def draw_main_screen(self, surface):
        bg_width, bg_height = self.assets.background.get_size()
        bg_x = (WIDTH - bg_width) // 2
        bg_y = (HEIGHT - bg_height) // 2
        surface.blit(self.assets.background, (bg_x, bg_y))
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))
        
        title = self.assets.fonts["title"].render("Ultimate Retro Emulator", True, WHITE)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, self.assets.margin * 2))
        
        if self.thumbnail:
            thumb_rect = self.thumbnail.get_rect(center=(
                WIDTH//2, 
                HEIGHT//2 - int(self.assets.base_size * 0.3)//2
            ))
            surface.blit(self.thumbnail, thumb_rect)
        
        self.carousel.draw(surface)
        
        instructions = [
            "Use ← → para navegar",
            "Enter para selecionar",
            "ESC para voltar",
            "C para configurações"
        ]
        
        for i, text in enumerate(instructions):
            instr = self.assets.fonts["info"].render(text, True, WHITE)
            surface.blit(instr, (
                WIDTH//2 - instr.get_width()//2,
                HEIGHT - int(self.assets.base_size * 0.3) - self.assets.margin * (len(instructions) - i + 1)
            ))
        
        copyright_text = self.assets.fonts["info"].render(
            "© 2025 Mickael Cypriano da Rocha - Todos os direitos reservados", 
            True, WHITE
        )
        surface.blit(copyright_text, (
            WIDTH//2 - copyright_text.get_width()//2,
            HEIGHT - self.assets.margin
        ))
        
        settings_rect = pygame.Rect(
            WIDTH - int(WIDTH * 0.15) - self.assets.margin,
            self.assets.margin,
            int(WIDTH * 0.15),
            self.assets.button_height
        )
        pygame.draw.rect(surface, MENU_BG, settings_rect, border_radius=5)
        settings_text = self.assets.fonts["menu"].render("Configurações", True, WHITE)
        surface.blit(settings_text, (
            settings_rect.x + (settings_rect.width - settings_text.get_width()) // 2,
            settings_rect.y + (settings_rect.height - settings_text.get_height()) // 2
        ))
    
    def run(self):
        self.update_thumbnail()
        self.last_selected = self.carousel.selected
        
        while self.running:
            self.handle_events()
            
            if WIDTH != screen.get_width() or HEIGHT != screen.get_height():
                self.update_sizes()
            
            # Check if platform selection changed
            if self.current_screen == "platforms" and self.carousel.selected != self.last_selected:
                self.update_thumbnail()
                self.last_selected = self.carousel.selected
            
            if self.current_screen == "platforms":
                self.carousel.update()
            elif self.current_screen == "games" and self.game_selection:
                self.game_selection.update()
            
            if self.current_screen == "platforms":
                self.draw_main_screen(screen)
            elif self.current_screen == "games" and self.game_selection:
                self.game_selection.draw(screen)
            
            self.settings.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    # Verificar e criar diretórios necessários
    Path("emuladores/ps2").mkdir(parents=True, exist_ok=True)
    Path("bios/ps2").mkdir(parents=True, exist_ok=True)
    Path("games/ps2").mkdir(parents=True, exist_ok=True)
    
    emulator = Emulator()
    emulator.run()
    pygame.quit()
    sys.exit()