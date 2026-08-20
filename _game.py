"""Loki — Life OS (Pygame)

Loop principal do jogo. Gerencia transições entre cenas:
  MENU → BUILDING → ROOM → CHAT → (voltar)

Stack: Pygame 2.x + FastAPI backend (API Base em settings.py).
"""
import os
import sys
import pygame
import pygame.font

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR, API_BASE
from api_client import ApiClient
from sprites import draw_text, draw_text_center, create_text_surface, text_size
from scenes.base_scene import BaseScene
from scenes.menu_scene import MenuScene
from scenes.building_scene import BuildingScene
from scenes.room_scene import RoomScene
from scenes.chat_scene import ChatScene


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        os.environ["SDL_VIDEODRIVER"] = "windows"
        pygame.display.set_caption("Loki — Life OS")

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "loki_icon_32.png")
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path).convert_alpha()
                pygame.display.set_icon(icon)
                print(f"Ícone carregado: {icon_path}")
            except Exception as e:
                print(f"Falha ao carregar ícone: {e}")

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.fonts = {
            "title": pygame.font.SysFont("monospace", 48, bold=True),
            "h1": pygame.font.SysFont("monospace", 32, bold=True),
            "h2": pygame.font.SysFont("monospace", 24, bold=True),
            "body": pygame.font.SysFont("monospace", 18),
            "small": pygame.font.SysFont("monospace", 14),
            "tiny": pygame.font.SysFont("monospace", 12),
        }

        self.api = ApiClient(API_BASE)
        self.current_scene: BaseScene | None = None
        self.previous_scene: BaseScene | None = None
        self.scene_stack = []

        self.change_scene(MenuScene(self))

    def change_scene(self, new_scene: BaseScene) -> None:
        if self.current_scene is not None:
            self.current_scene.on_exit()
            self.scene_stack.append(self.current_scene)
        self.current_scene = new_scene
        self.current_scene.on_enter()

    def pop_scene(self) -> None:
        if self.scene_stack:
            prev = self.scene_stack.pop()
            self.current_scene.on_exit()
            self.current_scene = prev
            self.current_scene.on_enter()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_scene is not None:
                            self.current_scene.on_esc()
                    elif event.key == pygame.K_F4 and event.mod & pygame.KMOD_ALT:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_scene is not None:
                        self.current_scene.on_mouse_down(event.pos)
                if self.current_scene is not None:
                    self.current_scene.handle_event(event)

            if self.current_scene is not None:
                self.current_scene.update(dt)

            self.screen.fill(BG_COLOR)
            if self.current_scene is not None:
                self.current_scene.draw(self.screen, self.fonts)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
