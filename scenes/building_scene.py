"""Cena do Prédio (Lobby) — lista de andares (salas).

Estilo: card pixel-art por andar, botão de novo andar, navegação para sala.
"""
import pygame
from sprites import draw_rect_aa, draw_button, draw_text_center, draw_simple_agent_sprite
from scenes.base_scene import BaseScene
from scenes.room_scene import RoomScene


class BuildingScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.floors = []
        self.hovered_floor = None
        self.floor_cards = []

    def on_enter(self):
        self.floors = self.game.api.get_floors()
        self.floors = sorted(self.floors, key=lambda f: f.get("order_index", 0))
        self.hovered_floor = None
        self.floor_cards = []

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.hovered_floor = None
        for fc in self.floor_cards:
            if fc["rect"].collidepoint(mx, my):
                self.hovered_floor = fc["data"]
                break

    def draw(self, screen, fonts):
        w, h = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT
        screen.fill((26, 26, 46))

        # Título
        title_rect = pygame.Rect(16, 16, 360, 48)
        draw_rect_aa(screen, title_rect, (15, 52, 96), border=2, border_color=(71, 85, 105),
                     shadow_offset=(4, 4))
        draw_text_center(screen, "PRÉDIO DOS ANDARES", fonts["h1"], title_rect)

        # Botão NOVO ANDAR
        btn_new = pygame.Rect(w - 150, 24, 130, 38)
        hover = btn_new.collidepoint(pygame.mouse.get_pos())
        draw_button(screen, btn_new, "+ NOVO ANDAR", fonts["body"],
                    normal_color=(15, 52, 96), hover_color=(22, 33, 62),
                    border_color=(74, 222, 128) if hover else (71, 85, 105),
                    hover_border=(74, 222, 128), text_color=(241, 245, 249))
        self.add_button(btn_new, "+ NOVO ANDAR", self._show_new_floor_dialog)

        # Grid 3 colunas
        start_y = 80
        cols = 3
        card_w = (w - 40) // cols - 12
        card_h = 200
        gap = 12

        for i, floor in enumerate(self.floors):
            if floor.get("is_archived"):
                continue
            row = i // cols
            col = i % cols
            x = 20 + col * (card_w + gap)
            y = start_y + row * (card_h + gap)
            rect = pygame.Rect(x, y, card_w, card_h)
            self.floor_cards.append({"rect": rect, "data": floor})

            color_hex = floor.get("color", "#4ade80")
            color_rgb = self.hex_to_rgb(color_hex)

            draw_rect_aa(screen, rect, (15, 52, 96), border=3, border_color=color_rgb,
                         shadow_offset=(4, 4))

            name = floor.get("name", "Sem nome")
            name_surf = fonts["h2"].render(name, True, (241, 245, 249))
            name_rect = name_surf.get_rect(center=(rect.centerx, y + 36))
            screen.blit(name_surf, name_rect)

            purpose = floor.get("purpose")
            if purpose:
                p_surf = fonts["small"].render(purpose, True, (148, 163, 184))
                p_rect = p_surf.get_rect(center=(rect.centerx, y + 64))
                screen.blit(p_surf, p_rect)

            status = floor.get("status_summary")
            if status:
                s_surf = fonts["tiny"].render(status, True, (100, 116, 139))
                s_rect = s_surf.get_rect(center=(rect.centerx, y + 90))
                screen.blit(s_surf, s_rect)

            # Agente label
            draw_text(screen, "AGENTE:", fonts["tiny"], (rect.x + 8, y + card_h - 30), (250, 204, 21))

            # Botão ENTRAR
            btn_y = y + card_h - 16
            btn_rect = pygame.Rect(rect.x, btn_y, rect.w, 14)
            is_hover = self.hovered_floor == floor
            draw_button(screen, btn_rect, "▶ ENTRAR", fonts["tiny"],
                        normal_color=(22, 33, 62), hover_color=(30, 41, 51),
                        border_color=color_rgb if is_hover else (71, 85, 105),
                        hover_border=color_rgb if is_hover else (71, 85, 105),
                        text_color=(241, 245, 249))
            self.add_button(btn_rect, f"ENTRAR", lambda f=floor: self._enter_floor(f))

        # Se não houver andares, mensagem
        if not self.floors:
            msg = "Nenhum andar criado. Clique em + NOVO ANDAR."
            msg_surf = fonts["body"].render(msg, True, (148, 163, 184))
            screen.blit(msg_surf, (w // 2 - msg_surf.get_width() // 2, h // 2))

        # Botão de voltar ao menu (ESC)
        draw_text(screen, "[ESC] Voltar ao menu", fonts["tiny"], (w - 160, h - 24), (100, 116, 139))

    def _enter_floor(self, floor):
        self.game.change_scene(RoomScene(self.game, floor))

    def _show_new_floor_dialog(self):
        new_floor = {
            "name": "",
            "purpose": "",
            "color": "#4ade80",
            "prompt": "",
        }
        self.game.change_scene(NewFloorDialogScene(self.game, new_floor))

    def hex_to_rgb(self, hex_str: str) -> tuple:
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 6:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return (74, 222, 128)


class NewFloorDialogScene(BaseScene):
    """Diálogo modal para criar novo andar."""
    def __init__(self, game, floor_data):
        super().__init__(game)
        self.floor_data = floor_data
        self.dialog_rect = None
        self.active_field = "name"
        self.cursor_blink = 0.0

    def on_enter(self):
        self.dialog_rect = pygame.Rect(
            (self.game.SCREEN_WIDTH - 440) // 2,
            (self.game.SCREEN_HEIGHT - 320) // 2,
            440, 320
        )
        self.active_field = "name"
        self.cursor_blink = 0.0

    def update(self, dt):
        self.cursor_blink += dt

    def draw(self, screen, fonts):
        w, h = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT

        # Fundo escuro atrás
        overlay = pygame.Surface((w, h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)
        screen.blit(overlay, (0, 0))

        dlg = self.dialog_rect
        draw_rect_aa(screen, dlg, (15, 52, 96), border=3, border_color=(250, 204, 21),
                     shadow_offset=(8, 8), shadow_color=(15, 23, 42))

        # Título
        draw_text_center(screen, "NOVO ANDAR", fonts["h2"], pygame.Rect(dlg.x, dlg.y, dlg.w, 40),
                         (250, 204, 21))

        f = self.floor_data
        y = dlg.y + 48

        # Nome
        draw_text(screen, "Nome:", fonts["body"], (dlg.x + 20, y), (241, 245, 249))
        name_rect = pygame.Rect(dlg.x + 70, y, dlg.w - 90, 28)
        draw_rect_aa(screen, name_rect, (22, 33, 62), border=1, border_color=(71, 85, 105))
        text_color = (226, 232, 240) if self.active_field == "name" else (148, 163, 184)
        draw_text(screen, f["name"], fonts["body"], (dlg.x + 76, y + 5), text_color)
        self.add_button(name_rect, "NAME", lambda: setattr(self, "active_field", "name"))

        y += 40

        # Propósito
        draw_text(screen, "Propósito:", fonts["body"], (dlg.x + 20, y), (241, 245, 249))
        purpose_rect = pygame.Rect(dlg.x + 70, y, dlg.w - 90, 36)
        draw_rect_aa(screen, purpose_rect, (22, 33, 62), border=1, border_color=(71, 85, 105))
        if f["purpose"]:
            draw_text(screen, f["purpose"], fonts["body"], (dlg.x + 76, y + 8), (226, 232, 240))
        self.add_button(purpose_rect, "PURPOSE", lambda: setattr(self, "active_field", "purpose"))

        y += 52

        # Cor
        draw_text(screen, "Cor:", fonts["body"], (dlg.x + 20, y), (241, 245, 249))
        color_rect = pygame.Rect(dlg.x + 70, y, 36, 22)
        color_rgb = self.hex_to_rgb(f["color"])
        draw_rect_aa(screen, color_rect, color_rgb, border=1, border_color=(71, 85, 105))

        colors = ["#4ade80", "#f472b6", "#818cf8", "#fb923c", "#34d399", "#facc15", "#e94560"]
        for i, c in enumerate(colors):
            cx = dlg.x + 120 + i * 38
            cy = y
            cc = self.hex_to_rgb(c)
            cr = pygame.Rect(cx, cy, 30, 22)
            draw_rect_aa(screen, cr, cc, border=1, border_color=(71, 85, 105))
            if c == f["color"]:
                pygame.draw.rect(screen, (250, 204, 21), cr, 2)
        y += 34

        # System Prompt
        draw_text(screen, "System Prompt:", fonts["body"], (dlg.x + 20, y), (241, 245, 249))
        prompt_rect = pygame.Rect(dlg.x + 20, y + 24, dlg.w - 40, 70)
        draw_rect_aa(screen, prompt_rect, (22, 33, 62), border=1, border_color=(71, 85, 105))
        prompt_text = f["prompt"] or "Você é o assistente virtual deste andar."
        draw_text(screen, prompt_text[:80] + ("..." if len(prompt_text) > 80 else ""),
                  fonts["tiny"], (dlg.x + 26, y + 30), (148, 163, 184))
        self.add_button(prompt_rect, "PROMPT", lambda: setattr(self, "active_field", "prompt"))

        y = dlg.y + dlg.h - 50

        # Botões
        btn_create = pygame.Rect(dlg.x + 20, y, 120, 32)
        btn_cancel = pygame.Rect(dlg.x + dlg.w - 140, y, 120, 32)
        draw_button(screen, btn_create, "CRIAR", fonts["body"],
                    normal_color=(22, 33, 62), hover_color=(30, 41, 51),
                    border_color=(74, 222, 128), hover_border=(74, 222, 128),
                    text_color=(241, 245, 249))
        draw_button(screen, btn_cancel, "CANCELAR", fonts["body"],
                    normal_color=(22, 33, 62), hover_color=(30, 41, 51),
                    border_color=(233, 69, 96), hover_border=(233, 69, 96),
                    text_color=(241, 245, 249))

    def on_mouse_down(self, pos):
        for btn in self.buttons:
            rect, label, callback = btn
            if rect.collidepoint(pos):
                callback()

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
