"""Cena do Menu Principal — TÍTULO + INICIAR + SAIR.

Estilo: título pixel art, efeito de scanline, botões arcade.
"""
import pygame
from scenes.base_scene import BaseScene
from scenes.building_scene import BuildingScene


class MenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.scanline_offset = 0.0

    def on_enter(self):
        self.scanline_offset = 0.0
        self.clear_buttons()

        # Botão INICIAR
        btn_start = pygame.Rect(0, 0, 320, 56)
        btn_start.center = (self.game.SCREEN_WIDTH // 2, self.game.SCREEN_HEIGHT - 180)
        self.add_button(btn_start, "INICIAR", self._start_game)

        # Botão SAIR
        btn_exit = pygame.Rect(0, 0, 200, 44)
        btn_exit.center = (self.game.SCREEN_WIDTH // 2, self.game.SCREEN_HEIGHT - 100)
        self.add_button(btn_exit, "SAIR", self._exit_game)

    def _start_game(self):
        self.game.change_scene(BuildingScene(self.game))

    def _exit_game(self):
        self.game.running = False

    def update(self, dt):
        self.scanline_offset += dt * 60

    def draw(self, screen, fonts):
        w, h = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        # Fundo
        screen.fill((26, 26, 46))

        # Scanlines (efeito CRT)
        for y in range(0, h, 4):
            if (y + int(self.scanline_offset) % 4) == 0:
                pygame.draw.line(screen, (20, 20, 36), (0, y), (w, y))

        # Título
        title = "LOKI"
        title_surf = fonts["title"].render(title, True, (250, 204, 21))
        title_rect = title_surf.get_rect(center=(w // 2, h // 3))
        screen.blit(title_surf, title_rect)

        # Subtítulo
        sub = "LIFE OS"
        sub_surf = fonts["h2"].render(sub, True, (148, 163, 184))
        sub_rect = sub_surf.get_rect(center=(w // 2, h // 3 + 50))
        screen.blit(sub_surf, sub_rect)

        # Linha decorativa abaixo do título
        line_y = title_rect.bottom + 30
        pygame.draw.line(screen, (71, 85, 105), (w // 2 - 120, line_y), (w // 2 + 120, line_y), 2)
        pygame.draw.line(screen, (250, 204, 21), (w // 2 - 120, line_y), (w // 2 + 120, line_y), 1)

        # Créditos
        credits_surf = fonts["small"].render("v0.1.0 — Gabriel", True, (100, 116, 139))
        screen.blit(credits_surf, (10, h - 20))

        # Botões com feedback de hover
        for rect, label, callback in self.buttons:
            is_hover = rect.collidepoint(mouse_pos)
            # Fundo do botão
            bg_color = (30, 41, 51) if is_hover else (15, 52, 96)
            border_color = (250, 204, 21) if is_hover else (71, 85, 105)
            # Sombra
            shadow = pygame.Rect(rect.x + 4, rect.y + 4, rect.w, rect.h)
            screen.fill((15, 23, 42), shadow)
            # Botão
            btn_rect = pygame.Rect(rect.x, rect.y, rect.w, rect.h)
            pygame.draw.rect(screen, bg_color, btn_rect)
            pygame.draw.rect(screen, border_color, btn_rect, 2)
            # Texto
            txt = fonts["body"].render(label, True, (241, 245, 249))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for rect, label, callback in self.buttons:
                if rect.collidepoint(pos):
                    callback()
