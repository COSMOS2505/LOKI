"""Cena base que todas as cenas herdam."""
from abc import ABC, abstractmethod
import pygame


class BaseScene(ABC):
    """Cena base com ciclo de vida: on_enter, update, draw, on_exit, on_esc."""

    def __init__(self, game: "Game"):
        self.game = game
        self.buttons = []  # Lista de botões [(rect, text, callback), ...]

    @abstractmethod
    def on_enter(self) -> None:
        """Chamado quando a cena entra. Carrega dados, prepara UI."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update frame a frame (dt em segundos)."""

    @abstractmethod
    def draw(self, screen: pygame.Surface, fonts: dict) -> None:
        """Desenha a cena."""

    def on_exit(self) -> None:
        """Chamado quando a cena sai. Cleanup."""

    def on_esc(self) -> None:
        """Chamado com Escape. Por padrão, tenta voltar ou fechar."""
        self.game.pop_scene()

    def on_mouse_down(self, pos: tuple) -> None:
        """Chamado com clique do mouse. Verifica botões."""
        for btn in self.buttons:
            rect, text, callback = btn
            if rect.collidepoint(pos):
                callback()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Hook para eventos específicos da cena."""

    def add_button(self, rect: pygame.Rect, text: str, callback) -> None:
        """Registra um botão dessa cena."""
        self.buttons.append((rect, text, callback))

    def clear_buttons(self) -> None:
        self.buttons.clear()
