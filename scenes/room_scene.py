"""Cena da Sala do Andar — ambiente 2D com agente NPC e widgets.

Layout:
  - Fundo: parede pixel art do quarto
  - Centro: mesa pixel art com agente NPC (clicável → chat)
  - Esquerda: widgets disponíveis + botão adicionar
  - Clique no agente abre ChatScene
"""
import pygame
from sprites import draw_rect_aa, draw_button, draw_text, draw_simple_agent_sprite, draw_text_center
from scenes.base_scene import BaseScene


class RoomScene(BaseScene):
    def __init__(self, game, floor):
        super().__init__(game)
        self.floor = floor
        self.widgets = []
        self.chat_open = False
        self.agent_rect = None  # Rect clicável do agente
        self.load_widgets()

    def on_enter(self):
        self.load_widgets()
        self.chat_open = False

    def load_widgets(self):
        self.widgets = self.game.api.get_widgets(self.floor["id"])

    def update(self, dt):
        pass

    def draw(self, screen, fonts):
        w, h = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT
        screen.fill((22, 33, 62))  # BG_SURFACE

        # Fundo: parede pixel
        self.draw_wallpaper(screen, w, h)

        # Mesa
        self.draw_table(screen, w, h)

        # Agente NPC na mesa (clicável)
        self.agent_rect = pygame.Rect(w // 2 - 30, h // 2 - 80, 60, 80)
        draw_simple_agent_sprite(screen, w // 2, h // 2 - 40, scale=3)
        self.add_button(self.agent_rect, "AGENTE", self._open_chat)

        # Agente label
        draw_text(screen, "AGENTE", fonts["tiny"], (w // 2 - 12, h // 2 + 40), (250, 204, 21))

        # Widgets na esquerda
        self.draw_widgets_panel(screen, fonts, w, h)

    def draw_wallpaper(self, screen, w, h):
        """Parede pixel art com padrão de quadrados."""
        tile = 32
        for y in range(0, h, tile):
            for x in range(0, w, tile):
                if (x // tile + y // tile) % 2 == 0:
                    color = (15, 52, 96)
                else:
                    color = (22, 33, 62)
                rect = pygame.Rect(x, y, tile, tile)
                draw_rect_aa(screen, rect, color, border=1, border_color=(10, 15, 30))

    def draw_table(self, screen, w, h):
        """Mesa pixel art no centro."""
        table_w, table_h = 200, 20
        table_x = w // 2 - table_w // 2
        table_y = h // 2 + 20

        # Pernas da mesa
        leg_w = 6
        leg_h = 30
        leg_l = pygame.Rect(table_x + 20, table_y + table_h, leg_w, leg_h)
        leg_r = pygame.Rect(table_x + table_w - 26, table_y + table_h, leg_w, leg_h)
        draw_rect_aa(screen, leg_l, (71, 85, 105), border=1, border_color=(51, 65, 85))
        draw_rect_aa(screen, leg_r, (71, 85, 105), border=1, border_color=(51, 65, 85))

        # Tabela
        table_rect = pygame.Rect(table_x, table_y, table_w, table_h)
        draw_rect_aa(screen, table_rect, (100, 116, 139), border=2, border_color=(71, 85, 105),
                     shadow_offset=(4, 4), shadow_color=(15, 23, 42))

    def draw_widgets_panel(self, screen, fonts, w, h):
        """Painel de widgets na esquerda."""
        panel_w = 180
        panel_h = h - 100
        panel_rect = pygame.Rect(10, 80, panel_w, panel_h)
        draw_rect_aa(screen, panel_rect, (15, 52, 96), border=2, border_color=(71, 85, 105),
                     shadow_offset=(4, 4))

        # Título
        draw_text_center(screen, "WIDGETS", fonts["h2"], panel_rect, (250, 204, 21), offset_y=-20)

        # Lista de widgets existentes
        y = panel_rect.y + 40
        if self.widgets:
            for widget in self.widgets:
                wtype = widget.get("widget_type", "desconhecido")
                label = self.widget_label(wtype)
                draw_text(screen, label, fonts["body"], (panel_rect.x + 10, y), (241, 245, 249))
                y += 24
        else:
            draw_text(screen, "Nenhum widget", fonts["small"], (panel_rect.x + 10, y), (100, 116, 139))
            y += 20

        # Botão adicionar widget
        add_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + panel_h - 40, panel_w - 20, 30)
        draw_button(screen, add_rect, "+ ADICIONAR", fonts["body"],
                    normal_color=(22, 33, 62), hover_color=(30, 41, 51),
                    border_color=(74, 222, 128), hover_border=(74, 222, 128),
                    text_color=(241, 245, 249))
        self.add_button(add_rect, "ADICIONAR_WIDGET", self._add_widget)

    def _open_chat(self):
        self.game.change_scene(ChatScene(self.game, self.floor))

    def _add_widget(self):
        # Diálogo simples para escolher widget
        self.add_widget_dialog = {
            "options": ["financeiro", "ordens", "posts", "docs"],
            "selected": 0,
        }

    def widget_label(self, wtype: str) -> str:
        labels = {
            "financeiro": "Financas",
            "ordens": "Ordens",
            "posts": "Posts",
            "docs": "Docs",
        }
        return labels.get(wtype, f"Widget: {wtype}")
