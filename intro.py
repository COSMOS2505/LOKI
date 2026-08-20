"""
LOKI - Tela de Introducao (Parte 1)
====================================
Andares em pixel-art, scroll, NPCs no chao, ciclo dia/noite.
Sem telhado, sem chamine, sem circulos ao redor.
"""

import pygame
import sys
import time
import math
import random
import os
import glob

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
BUILDING_W = 360  # largura na tela (escalada)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("LOKI")
clock = pygame.time.Clock()

FONT_TITLE = pygame.font.Font(None, 72)
FONT_SUB = pygame.font.Font(None, 28)
FONT_BTN = pygame.font.Font(None, 36)
FONT_SM = pygame.font.Font(None, 22)

BLACK=(0,0,0); WHITE=(255,255,255); GOLD=(255,200,50); DARK_GREEN=(34,85,34)
SKIN=(255,218,185); HAIR=(101,55,0); BLUE_EYE=(50,100,200); TUNIC=(85,107,47)
TUNIC_BELT=(60,80,30); PANTS=(101,67,33); BOOT=(30,20,10)
RED=(200,50,50); DARK_RED=(139,0,0); GREEN_FLAG=(34,100,34)
STONE=(150,150,150); DARK_STONE=(100,100,100); DARKER_STONE=(70,70,70)
WOOD=(101,67,33); DARK_WOOD=(60,40,20); DARKER_WOOD=(40,25,10)
BEIGE=(230,210,170); PLASTE=(210,190,150); WINDOW_LIT=(255,220,100)
WINDOW_DAY=(135,206,235); ROOF=(50,50,70); ROOF_DARK=(35,35,50)
BROWN_BRICK=(139,90,43); TAN=(210,180,140); DARK_BROWN=(80,50,20)

def get_sky_palette(hour):
    if 6<=hour<12: return {"top":(135,206,250),"mid":(200,230,255),"bottom":(255,240,200),"moon":False}
    elif 12<=hour<17: return {"top":(70,130,200),"mid":(180,210,240),"bottom":(255,220,180),"moon":False}
    elif 17<=hour<19: return {"top":(40,30,80),"mid":(200,100,80),"bottom":(255,150,50),"moon":True}
    else: return {"top":(15,10,40),"mid":(30,25,60),"bottom":(50,40,80),"moon":True}

def draw_sky(screen, hour):
    pal = get_sky_palette(hour)
    for y in range(SCREEN_H):
        if y<SCREEN_H//2:
            t=y/(SCREEN_H//2)
            r=int(pal["top"][0]*(1-t)+pal["mid"][0]*t)
            g=int(pal["top"][1]*(1-t)+pal["mid"][1]*t)
            b=int(pal["top"][2]*(1-t)+pal["mid"][2]*t)
        else:
            t=(y-SCREEN_H//2)/(SCREEN_H//2)
            r=int(pal["mid"][0]*(1-t)+pal["bottom"][0]*t)
            g=int(pal["mid"][1]*(1-t)+pal["bottom"][1]*t)
            b=int(pal["mid"][2]*(1-t)+pal["bottom"][2]*t)
        pygame.draw.line(screen,(r,g,b),(0,y),(SCREEN_W,y))
    if pal["moon"]:
        pygame.draw.circle(screen,(240,240,220),(SCREEN_W-150,100),40)
        pygame.draw.circle(screen,(200,200,180),(SCREEN_W-140,95),35)
        for i in range(30):
            sx=(i*137+50)%SCREEN_W; sy=(i*89+30)%(SCREEN_H//2)
            pygame.draw.circle(screen,WHITE,(sx,sy),2)
    else:
        pygame.draw.circle(screen,(255,240,100),(200,120),50)

# ═══════════════════════════════════════════════════════════════════════
# CARREGAR ANDARES
# ═══════════════════════════════════════════════════════════════════════

def load_floor_sprites():
    """Carrega todos os andar_*.png da pasta assets/ e padroniza a altura."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "assets")
    files = sorted(glob.glob(os.path.join(asset_path, "andar_*.png")))
    
    TARGET_H = 150  # altura fixa em pixels para cada andar
    
    sprites = []
    for f in files:
        img = pygame.image.load(f).convert_alpha()
        w, h = img.get_size()
        # Escala para BUILDING_W de largura, altura fixa TARGET_H
        img_scaled = pygame.transform.scale(img, (BUILDING_W, TARGET_H))
        sprites.append(img_scaled)
        print(f"  Carregado: {os.path.basename(f)} ({w}x{h} -> {BUILDING_W}x{TARGET_H})")
    
    return sprites

def world_to_screen(y, scroll_y):
    return y + scroll_y

def calculate_total_height(floors, overlap_ratio=0.12):
    """Calcula altura total dos andares considerando sobreposição."""
    if not floors:
        return 0
    total = floors[0].get_height()
    for i in range(1, len(floors)):
        h = floors[i].get_height()
        prev_h = floors[i-1].get_height()
        overlap = int(prev_h * overlap_ratio)
        total += h - overlap
    return total

def draw_building(screen, floors, hour, frame, scroll_y, floor_sprites):
    """Desenha o prédio com sprites de imagem."""
    # Calcula altura total
    total_h = len(floors) * 150  # TARGET_H = 150
    bx = (SCREEN_W - BUILDING_W) // 2
    
    # Coordenadas do mundo
    ground_y = SCREEN_H - 120
    floor_base_y = ground_y  # base dos andares começa no chão
    
    # --- CHAO ---
    sy = world_to_screen(ground_y, scroll_y)
    pygame.draw.rect(screen, (100,100,100), (0, sy, SCREEN_W, 120))
    pygame.draw.rect(screen, (60,60,60), (0, sy+50, SCREEN_W, 70))
    for fx in range(0, SCREEN_W, 60):
        pygame.draw.rect(screen, (200,200,100), (fx, sy+80, 30, 6))
    
    # --- ANDARES (sem sobreposição) ---
    current_y = floor_base_y
    for i, img in enumerate(floors):
        h = img.get_height()
        screen_y = world_to_screen(current_y - h, scroll_y)
        screen.blit(img, (bx, screen_y))
        current_y -= h
    
    return ground_y

def draw_npc(screen, x, y, frame, direction=1):
    p = 3
    for dx in range(-4,5):
        for dy in range(-6,0):
            if abs(dx)<=3 and dy>=-5:
                pygame.draw.rect(screen, HAIR, (x+dx*p, y+dy*p, p, p))
    for dx in range(-5,6):
        for dy in range(-4,2):
            if abs(dx)>=3 and abs(dx)<=4:
                pygame.draw.rect(screen, HAIR, (x+dx*p, y+dy*p, p, p))
    for dx in range(-3,4):
        for dy in range(-4,2):
            if abs(dx)<=2 and dy>=-3:
                pygame.draw.rect(screen, SKIN, (x+dx*p, y+dy*p, p, p))
    pygame.draw.rect(screen, BLUE_EYE, (x-1*p, y-2*p, p, p))
    pygame.draw.rect(screen, BLUE_EYE, (x+1*p, y-2*p, p, p))
    for dx in range(-3,4):
        for dy in range(2,8):
            pygame.draw.rect(screen, TUNIC, (x+dx*p, y+dy*p, p, p))
    for dx in range(-3,4):
        pygame.draw.rect(screen, TUNIC_BELT, (x+dx*p, y+7*p, p, p))
    pygame.draw.rect(screen, GOLD, (x-1*p, y+7*p, 2*p, p))
    for dy in range(3,7):
        pygame.draw.rect(screen, TUNIC, (x-4*p, y+dy*p, p, p))
    pygame.draw.rect(screen, SKIN, (x-4*p, y+7*p, p, p))
    for dy in range(3,7):
        pygame.draw.rect(screen, TUNIC, (x+4*p, y+dy*p, p, p))
    pygame.draw.rect(screen, SKIN, (x+4*p, y+7*p, p, p))
    leg = math.sin(frame*0.15)*2
    for dy in range(8,13):
        lx = x-2*p+int(leg)*p
        pygame.draw.rect(screen, PANTS, (lx, y+dy*p, p, p))
    for dy in range(8,13):
        rx = x+2*p-int(leg)*p
        pygame.draw.rect(screen, PANTS, (rx, y+dy*p, p, p))
    pygame.draw.rect(screen, BOOT, (x-2*p+int(leg)*p, y+13*p, 2*p, p))
    pygame.draw.rect(screen, BOOT, (x+2*p-int(leg)*p, y+13*p, 2*p, p))

def draw_button(screen, x, y, text, hovered, frame, color=DARK_GREEN):
    padding_x, padding_y = 24, 12
    text_surf = FONT_BTN.render(text, True, WHITE)
    w = text_surf.get_width() + padding_x*2
    h = text_surf.get_height() + padding_y*2
    if hovered:
        glow = abs(math.sin(frame*0.1))*30
        if color == DARK_GREEN:
            c = (80+glow, 200+glow, 80+glow)
            border = (150+glow, 255, 150+glow)
        else:
            c = (80+glow, 80+glow, 200+glow)
            border = (150+glow, 150+glow, 255)
    else:
        c = color
        border = (100,200,100) if color==DARK_GREEN else (100,100,200)
    pygame.draw.rect(screen, c, (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, border, (x, y, w, h), 3, border_radius=8)
    screen.blit(text_surf, (x+padding_x, y+padding_y))
    return w, h

def main():
    frame = 0
    running = True
    entering = False
    enter_timer = 60
    scroll_y = 0
    
    print("Carregando andares...")
    floor_sprites = load_floor_sprites()
    if not floor_sprites:
        print("ERRO: Nenhum andar encontrado em assets/andar_*.png")
        sys.exit(1)
    
    print(f"Total: {len(floor_sprites)} andares carregados")
    
    building_floors = [random.choice(floor_sprites), random.choice(floor_sprites)]
    
    npc_data = [
        {"x":100, "world_y":SCREEN_H-140, "speed":1.5, "dir":1, "off":0},
        {"x":400, "world_y":SCREEN_H-140, "speed":1.0, "dir":-1, "off":20},
        {"x":700, "world_y":SCREEN_H-140, "speed":1.2, "dir":1, "off":40},
    ]
    
    while running:
        frame += 1
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
                elif event.button == 4:  # rodinha pra cima: camera desce (ver chão)
                    scroll_y = min(scroll_y + 80, max(0, calculate_total_height(building_floors) + 3*150 - SCREEN_H + 200))
                elif event.button == 5:  # rodinha pra baixo: camera sobe (ver topo)
                    scroll_y = max(0, scroll_y - 80)
        
        add_w = FONT_BTN.render("ADICIONAR ANDAR", True, WHITE).get_width() + 48
        add_h = FONT_BTN.render("ADICIONAR ANDAR", True, WHITE).get_height() + 24
        enter_w = FONT_BTN.render("ENTER", True, WHITE).get_width() + 48
        enter_h = FONT_BTN.render("ENTER", True, WHITE).get_height() + 24
        
        btn_x = SCREEN_W - max(add_w, enter_w) - 30
        btn_add_x = btn_x
        btn_add_y = SCREEN_H // 2 - 60
        btn_enter_x = btn_x
        btn_enter_y = SCREEN_H // 2 + 10
        
        hover_add = (btn_add_x <= mouse_pos[0] <= btn_add_x+add_w and
                     btn_add_y <= mouse_pos[1] <= btn_add_y+add_h)
        hover_enter = (btn_enter_x <= mouse_pos[0] <= btn_enter_x+enter_w and
                       btn_enter_y <= mouse_pos[1] <= btn_enter_y+enter_h)
        
        if clicked and hover_add and not entering:
            next_idx = len(building_floors) % len(floor_sprites)
            building_floors.append(floor_sprites[next_idx])
            # Auto-scroll para mostrar o novo andar (topo)
            total_h = len(building_floors) * 150
            max_scroll = max(0, total_h + 3*150 - SCREEN_H + 200)
            scroll_y = max_scroll
        
        if clicked and hover_enter and not entering:
            entering = True
            enter_timer = 60
        if entering:
            enter_timer -= 1
            if enter_timer <= 0:
                print(f"ENTRANDO! Andares: {len(building_floors)}")
                entering = False
        
        current_hour = time.localtime().tm_hour
        
        draw_sky(screen, current_hour)
        ground_y = draw_building(screen, building_floors, current_hour, frame, scroll_y, floor_sprites)
        
        for npc in npc_data:
            npc["x"] += npc["speed"] * npc["dir"]
            if npc["x"] > SCREEN_W-100: npc["dir"] = -1
            elif npc["x"] < 50: npc["dir"] = 1
            npc_screen_y = world_to_screen(npc["world_y"], scroll_y)
            draw_npc(screen, int(npc["x"]), npc_screen_y, frame+npc["off"], npc["dir"])
        
        title = FONT_TITLE.render("LOKI", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_W//2, 35)))
        sub = FONT_SUB.render("LIFE OS", True, WHITE)
        screen.blit(sub, sub.get_rect(center=(SCREEN_W//2, 80)))
        
        screen.blit(FONT_SM.render(f"Andares: {len(building_floors)}", True, WHITE), (10,10))
        screen.blit(FONT_SM.render(f"{current_hour:02d}:00", True, WHITE), (10,30))
        
        if not entering:
            draw_button(screen, btn_add_x, btn_add_y, "ADICIONAR ANDAR", hover_add, frame, DARK_GREEN)
            draw_button(screen, btn_enter_x, btn_enter_y, "ENTER", hover_enter, frame, (34,85,170))
        else:
            ent = FONT_BTN.render("ENTRANDO...", True, GOLD)
            screen.blit(ent, ent.get_rect(center=(SCREEN_W//2, btn_enter_y+enter_h//2)))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
