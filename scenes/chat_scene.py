"""Cena do Chat — painel de conversa com o agente NPC.

Layout:
  - Painel flutuante no centro (janela modal)
  - Header com nome do agente
  - Lista de mensagens (scroll)
  - Input de texto no fundo
  - Envio via API
"""
import pygame
from sprites import draw_rect_aa, draw_button, draw_text, draw_text_center
from scenes.base_scene import BaseScene


class ChatScene(BaseScene):
    def __init__(self, game, floor):
        super().__init__(game)
        self.floor = floor
        self.messages = []
        self.input_text = ""
        self.scroll_offset = 0
        self.load_messages()

    def on_enter(self):
        self.load_messages()
        self.input_text = ""
        self.scroll_offset = 0

    def load_messages(self):
        self.messages = self.game.api.get_chat_history(self.floor["id"])

    def update(self, dt):
        # Scroll automático para o final quando nova mensagem
        pass

    def draw(self, screen, fonts):
        w, h = self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT
        screen.fill((26, 26, 46))

        # Painel do chat
        panel_w = 520
        panel_h = 480
        panel_rect = pygame.Rect((w - panel_w) // 2, (h - panel_h) // 2, panel_w, panel_h)
        draw_rect_aa(screen, panel_rect, (15, 52, 96), border=3, border_color=(250, 204, 21),
                     shadow_offset=(8, 8), shadow_color=(15, 23, 42))

        # Header
        header_rect = pygame.Rect(panel_rect.x, panel_rect.y, panel_w, 48)
        draw_rect_aa(screen, header_rect, (22, 33, 62), border=0)
        draw_text(screen, "AGENTE", fonts["h2"], (panel_rect.x + 16, panel_rect.y + 12), (250, 204, 21))
        floor_name = self.floor.get("name", "Sala")
        draw_text(screen, floor_name, fonts["body"], (panel_rect.x + 80, panel_rect.y + 12), (241, 245, 249))

        # Botão fechar (X)
        close_rect = pygame.Rect(panel_rect.x + panel_w - 30, panel_rect.y + 12, 24, 24)
        draw_button(screen, close_rect, "X", fonts["body"],
                    normal_color=(22, 33, 62), hover_color=(233, 69, 96),
                    border_color=(71, 85, 105), hover_border=(233, 69, 96),
                    text_color=(241, 245, 249))
        self.add_button(close_rect, "CLOSE_CHAT", self._close_chat)

        # Lista de mensagens
        msg_area = pygame.Rect(panel_rect.x + 12, panel_rect.y + 52, panel_w - 24, panel_h - 100)
        draw_rect_aa(screen, msg_area, (10, 15, 30), border=1, border_color=(71, 85, 105))

        # Renderizar mensagens
        self.draw_messages(screen, fonts, msg_area)

        # Input
        input_rect = pygame.Rect(panel_rect.x + 12, panel_rect.y + panel_h - 40, panel_w - 100, 32)
        draw_rect_aa(screen, input_rect, (22, 33, 62), border=2, border_color=(71, 85, 105),
                     shadow_offset=(2, 2), shadow_color=(15, 23, 42))
        draw_text(screen, self.input_text, fonts["body"], (input_rect.x + 8, input_rect.y + 6), (241, 245, 249))

        # Botão enviar
        send_rect = pygame.Rect(panel_rect.x + panel_w - 72, panel_rect.y + panel_h - 40, 60, 32)
        draw_button(screen, send_rect, "ENVIAR", fonts["body"],
                    normal_color=(74, 222, 128), hover_color=(52, 211, 153),
                    border_color=(74, 222, 128), hover_border=(52, 211, 153),
                    text_color=(15, 23, 42))
        self.add_button(send_rect, "SEND_MESSAGE", self._send_message)

    def draw_messages(self, screen, fonts, area):
        """Renderiza as mensagens com scroll."""
        y = area.y + 8
        line_h = 22
        max_h = area.h - 16

        # As mensagens mais recentes vão no fundo; mostra as últimas N
        messages_to_show = self.messages[-20:] if len(self.messages) > 20 else self.messages

        for msg in messages_to_show:
            role = msg.get("role", "agent")
            content = msg.get("content", "")
            is_user = role == "user"
            color = (241, 245, 249) if is_user else (74, 222, 128)
            bg = (22, 33, 62) if is_user else (15, 52, 96)

            # Label de papel
            label = "VOCÊ" if is_user else "AGENTE"
            label_surf = fonts["tiny"].render(label, True, color)
            screen.blit(label_surf, (area.x + 4, y))

            # Mensagem
            msg_lines = self.wrap_text(content, fonts["body"], area.w - 80)
            for line in msg_lines[:3]:  # máx 3 linhas
                draw_text(screen, line, fonts["body"], (area.x + 44, y), color)
                y += line_h
            y += 4

            if y > area.y + area.h - 30:
                break

    def wrap_text(self, text, font, max_width):
        """Quebra texto em linhas."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _close_chat(self):
        self.game.pop_scene()

    def _send_message(self):
        text = self.input_text.strip()
        if not text:
            return
        # Salvar apenas como agente (resposta placeholder — API ainda não responde IA real)
        msg = {
            "role": "user",
            "content": text,
            "floor_id": self.floor["id"],
            "created_at": "2026-08-19T00:00:00Z",
        }
        self.game.api.send_chat(self.floor["id"], text)
        self.messages.append(msg)
        self.input_text = ""
        # Resposta placeholder do agente
        agent_reply = {
            "role": "agent",
            "content": f"[Agente da sala '{self.floor.get('name', 'Sala')}'] Recebido: {text}",
            "floor_id": self.floor["id"],
            "created_at": "2026-08-19T00:00:01Z",
        }
        self.messages.append(agent_reply)


# import ok via linha 4