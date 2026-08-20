"""Renderização de sprites pixel art com Pygame.

Converte rect, textos e sprites SVG em superfícies pixel-art escaladas.
"""
import pygame
import math
from typing import Optional
from settings import (
    BG_COLOR, BG_SURFACE, BG_CARD, GOLD, AGENT_GREEN, ACCENT_RED,
    GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500, GRAY_600,
    GRAY_700, GRAY_800, API_BASE
)


def pixel_scale(surface: pygame.Surface, scale: int) -> pygame.Surface:
    """Escala uma surface mantendo o aspecto pixel-art."""
    scaled = pygame.transform.scale(surface, (surface.get_width() * scale, surface.get_height() * scale))
    return scaled


def draw_rect_aa(surface: pygame.Surface, rect: pygame.Rect, color: tuple, border: int = 0,
                 border_color: Optional[tuple] = None, shadow_offset: tuple = (0, 0),
                 shadow_color: Optional[tuple] = None) -> None:
    if shadow_color and shadow_offset != (0, 0):
        sh_rect = pygame.Rect(rect.x + shadow_offset[0], rect.y + shadow_offset[1],
                              rect.w, rect.h)
        pygame.draw.rect(surface, shadow_color, sh_rect)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border)
    else:
        pygame.draw.rect(surface, color, rect)


def draw_button(surface: pygame.Surface, rect: pygame.Rect, text: str,
                font: pygame.font.Font, normal_color: tuple = BG_CARD,
                hover_color: tuple = BG_SURFACE, border_color: tuple = GRAY_700,
                hover_border: tuple = GOLD, text_color: tuple = GRAY_100,
                shadow_offset: tuple = (4, 4)) -> bool:
    mouse = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]
    hover = rect.collidepoint(mouse)

    bg = hover_color if hover else normal_color
    brd = hover_border if hover else border_color

    if shadow_offset != (0, 0):
        sh = pygame.Rect(rect.x + shadow_offset[0], rect.y + shadow_offset[1], rect.w, rect.h)
        surface.fill((15, 23, 42), sh)

    draw_rect_aa(surface, rect, bg, border=2, border_color=brd,
                 shadow_offset=shadow_offset, shadow_color=(15, 23, 42))
    draw_text_center(surface, text, font, rect, text_color)
    return hover and clicked


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              pos: tuple, color: tuple = GRAY_100, align: str = "left") -> None:
    surf = font.render(text, True, color)
    if align == "center":
        surface.blit(surf, pos)
    elif align == "right":
        surface.blit(surf, (pos[0] - surf.get_width(), pos[1]))
    else:
        surface.blit(surf, pos)


def draw_text_center(surface: pygame.Surface, text: str, font: pygame.font.Font,
                     rect: pygame.Rect, color: tuple = GRAY_100,
                     offset_y: int = 0) -> None:
    surf = font.render(text, True, color)
    x = rect.x + (rect.w - surf.get_width()) // 2
    y = rect.y + (rect.h - surf.get_height()) // 2 + offset_y
    surface.blit(surf, (x, y))


def draw_filled_arc(surface: pygame.Surface, color: tuple, rect: pygame.Rect,
                    start_angle: float, stop_angle: float, thickness: int = 2) -> None:
    steps = max(8, int((stop_angle - start_angle) / math.radians(2)))
    for i in range(steps):
        a1 = start_angle + (stop_angle - start_angle) * i / steps
        a2 = start_angle + (stop_angle - start_angle) * (i + 1) / steps
        p1 = (rect.x + rect.w // 2 + math.cos(a1) * rect.w // 2,
              rect.y + rect.h // 2 + math.sin(a1) * rect.h // 2)
        p2 = (rect.x + rect.w // 2 + math.cos(a2) * rect.w // 2,
              rect.y + rect.h // 2 + math.sin(a2) * rect.h // 2)
        pygame.draw.line(surface, color, p1, p2, thickness)


def draw_progress_bar(surface: pygame.Surface, rect: pygame.Rect, percent: float,
                      fg_color: tuple = GOLD, bg_color: tuple = GRAY_800,
                      border_color: tuple = GRAY_700) -> None:
    draw_rect_aa(surface, rect, bg_color, border=2, border_color=border_color,
                 shadow_offset=(4, 4))
    inner = rect.inflate(-4, -4)
    fill_w = max(0, int(inner.w * percent))
    if fill_w > 0:
        fill_rect = pygame.Rect(inner.x, inner.y, fill_w, inner.h)
        draw_rect_aa(surface, fill_rect, fg_color, border=0)


def draw_simple_agent_sprite(surface: pygame.Surface, x: int, y: int, scale: int = 4,
                              eye_glow: bool = True) -> None:
    """Desenha sprite pixel-art de agente (lobo fantasy estilo 8-bit)."""
    body_w, body_h = 12 * scale, 16 * scale
    body_rect = pygame.Rect(x - body_w // 2, y - body_h + 4 * scale, body_w, body_h)
    draw_rect_aa(surface, body_rect, (244, 162, 97), border=2,
                 border_color=GRAY_700, shadow_offset=(3 * scale, 3 * scale),
                 shadow_color=(15, 23, 42))

    head_size = 10 * scale
    head_rect = pygame.Rect(x - head_size // 2, y - body_h - 2 * scale, head_size, head_size)
    draw_rect_aa(surface, head_rect, (244, 162, 97), border=2,
                 border_color=GRAY_700, shadow_offset=(3 * scale, 3 * scale),
                 shadow_color=(15, 23, 42))

    eye_size = 3 * scale
    eye_rect = pygame.Rect(x - eye_size, y - body_h - 3 * scale, eye_size * 2, eye_size * 2)
    draw_rect_aa(surface, eye_rect, (96, 165, 250), border=0)
    if eye_glow:
        glow = pygame.Rect(x - eye_size - 1, y - body_h - 3 * scale - 1, eye_size * 2 + 2, eye_size * 2 + 2)
        draw_rect_aa(surface, glow, (96, 165, 250), border=0, shadow_offset=(0, 0),
                     shadow_color=(96, 165, 250))

    ear_l = pygame.Rect(x - head_size // 2 - 1 * scale, y - body_h - 4 * scale, 2 * scale, 4 * scale)
    draw_rect_aa(surface, ear_l, (244, 162, 97), border=1, border_color=GRAY_700)
    ear_r = pygame.Rect(x + head_size // 2 - 1 * scale, y - body_h - 4 * scale, 2 * scale, 4 * scale)
    draw_rect_aa(surface, ear_r, (244, 162, 97), border=1, border_color=GRAY_700)

    tail_points = [
        (x + body_w // 2, y - body_h + 8 * scale),
        (x + body_w // 2 + 3 * scale, y - body_h + 6 * scale),
        (x + body_w // 2 + 5 * scale, y - body_h + 8 * scale),
    ]
    pygame.draw.lines(surface, (244, 162, 97), False, tail_points, 2 * scale)

    leg_l = pygame.Rect(x - body_w // 2 + 1 * scale, y - 2 * scale, 3 * scale, 4 * scale)
    draw_rect_aa(surface, leg_l, (244, 162, 97), border=1, border_color=GRAY_700)
    leg_r = pygame.Rect(x + body_w // 2 - 4 * scale, y - 2 * scale, 3 * scale, 4 * scale)
    draw_rect_aa(surface, leg_r, (244, 162, 97), border=1, border_color=GRAY_700)


def create_text_surface(text: str, font: pygame.font.Font, color: tuple = GRAY_100) -> pygame.Surface:
    return font.render(text, True, color)


def text_size(text: str, font: pygame.font.Font) -> tuple:
    return font.size(text)
