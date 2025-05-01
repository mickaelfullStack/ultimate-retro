import os
import sys
import pygame
from pygame.locals import *

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
    emulator = Emulator()
    emulator.run()
    pygame.quit()
    sys.exit()