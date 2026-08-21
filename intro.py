"""
LOKI - Introducao (Parte 1)
Andares pixel-art, scroll, NPCs na calcada, ciclo dia/noite.
Clique no predio para abrir a sala do andar.
"""

import pygame
import sys
import time
import math
import os
import glob
import urllib.request
import urllib.error
import json
import threading

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
BUILDING_W = 360

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("LOKI")
clock = pygame.time.Clock()

FONT_TITLE = pygame.font.Font(None, 72)
FONT_SUB = pygame.font.Font(None, 28)
FONT_BTN = pygame.font.Font(None, 36)
FONT_SM = pygame.font.Font(None, 22)
FONT_CHAT = pygame.font.Font(None, 24)

BLACK=(0,0,0); WHITE=(255,255,255); GOLD=(255,200,50); DARK_GREEN=(34,85,34)
SKIN=(255,218,185); BLUE_EYE=(50,100,200); BOOT=(30,20,10)
CHAT_BG = (30, 30, 50, 230); CHAT_BORDER = (100, 100, 150); CHAT_INPUT_BG = (50, 50, 80)

STYLE_NAMES = {
    0: "Art Deco", 1: "Hobbit", 2: "Medieval", 3: "Moderna",
    4: "Oscar Niemeyer", 5: "Portuguesa", 6: "Retro Futuristico",
    7: "Romana", 8: "StarWars", 9: "Terreno Taruma", 10: "Template Branco"
}

def draw_sky(screen, hour):
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        r = int(15 + t * 30); g = int(10 + t * 25); b = int(40 + t * 40)
        pygame.draw.line(screen,(r,g,b),(0,y),(SCREEN_W,y))
    pygame.draw.circle(screen,(240,240,220),(SCREEN_W-150,100),40)
    pygame.draw.circle(screen,(200,200,180),(SCREEN_W-140,95),35)

def load_floor_sprites():
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "assets")
    style_files = [
        "1_Art Deco.png", "2_Hobbit.png", "3_Medieval.png", "4_Moderna.png",
        "5_Oscar Niemeyer.png", "6_Portuguesa.png", "7_Retro Futuristico.png",
        "8_Romana.png", "9_StarWars.png", "10_Tarumã.png", "11_Template_Branco.png"
    ]
    sprites = []
    for fname in style_files:
        fpath = os.path.join(asset_path, fname)
        if os.path.exists(fpath):
            img = pygame.image.load(fpath).convert_alpha()
            w, h = img.get_size()
            scale = BUILDING_W / w
            new_h = int(h * scale)
            sprites.append(pygame.transform.scale(img, (BUILDING_W, new_h)))
    
    construction = None
    con_path = os.path.join(asset_path, "0_Construction.png")
    if os.path.exists(con_path):
        img = pygame.image.load(con_path).convert_alpha()
        w, h = img.get_size()
        scale = BUILDING_W / w
        new_h = int(h * scale)
        construction = pygame.transform.scale(img, (BUILDING_W, new_h))
    
    return sprites, construction

def chat_with_ia(messages, building_floors, model="qwen2.5:1.5b"):
    try:
        url = "http://localhost:11434/api/chat"
        
        andares_info = []
        for i, floor in enumerate(building_floors):
            if isinstance(floor, dict):
                nome = floor.get("nome", f"Andar {i+1}")
            else:
                nome = f"Andar {i+1}"
            andares_info.append(f"  - {nome}")
        
        andares_text = "\n".join(andares_info) if andares_info else "  (vazio)"
        
        system_content = (
            "Voce eh o sindico do predio LOKI, localizado em Aveiro, Portugal.\n"
            "Cada andar representa um projeto em decorrencia.\n"
            f"Andares atuais: {len(building_floors)}\n"
            f"{andares_text}\n"
            "Responda em portugues de Portugal. Seja conciso (max 3-4 linhas).\n"
            "NUNCA invente informacoes. Se nao souber, diga 'Nao tenho essa informacao'."
        )
        
        system_prompt = {"role": "system", "content": system_content}
        full_messages = [system_prompt] + [m for m in messages if m["role"] != "system"]
        
        payload = {
            "model": model, "messages": full_messages, "stream": False,
            "options": {"num_ctx": 2048, "num_gpu": 0}
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["message"]["content"]
    
    except urllib.error.URLError:
        return "[Erro: Ollama nao esta rodando. Inicie com: ollama serve]"
    except Exception as e:
        return f"[Erro: {str(e)}]"

def chat_async(messages, chat_messages, building_floors):
    try:
        resposta = chat_with_ia(messages, building_floors)
        chat_messages.append({"role": "assistant", "content": resposta})
    except Exception as e:
        chat_messages.append({"role": "assistant", "content": f"[Erro: {str(e)}]"})

def draw_npc_walking(screen, x, ground_y, frame, off, hair, tunic, pants):
    p = 3
    leg = math.sin((frame + off) * 0.15) * 2
    
    for dx in range(-4, 5):
        for dy in range(-6, 0):
            if abs(dx) <= 3 and dy >= -5:
                pygame.draw.rect(screen, hair, (int(x) + dx*p, ground_y - 60 + dy*p, p, p))
    for dx in range(-5, 6):
        for dy in range(-4, 2):
            if abs(dx) >= 3 and abs(dx) <= 4:
                pygame.draw.rect(screen, hair, (int(x) + dx*p, ground_y - 60 + dy*p, p, p))
    
    for dx in range(-3, 4):
        for dy in range(-4, 2):
            if abs(dx) <= 2 and dy >= -3:
                pygame.draw.rect(screen, SKIN, (int(x) + dx*p, ground_y - 60 + dy*p, p, p))
    
    pygame.draw.rect(screen, BLUE_EYE, (int(x) - 1*p, ground_y - 60 - 2*p, p, p))
    pygame.draw.rect(screen, BLUE_EYE, (int(x) + 1*p, ground_y - 60 - 2*p, p, p))
    
    for dx in range(-3, 4):
        for dy in range(2, 8):
            pygame.draw.rect(screen, tunic, (int(x) + dx*p, ground_y - 60 + dy*p, p, p))
    
    for dx in range(-3, 4):
        pygame.draw.rect(screen, (max(0, tunic[0]-25), max(0, tunic[1]-25), max(0, tunic[2]-25)), (int(x) + dx*p, ground_y - 60 + 7*p, p, p))
    pygame.draw.rect(screen, GOLD, (int(x) - 1*p, ground_y - 60 + 7*p, 2*p, p))
    
    for dy in range(3, 7):
        pygame.draw.rect(screen, tunic, (int(x) - 4*p, ground_y - 60 + dy*p, p, p))
    pygame.draw.rect(screen, SKIN, (int(x) - 4*p, ground_y - 60 + 7*p, p, p))
    for dy in range(3, 7):
        pygame.draw.rect(screen, tunic, (int(x) + 4*p, ground_y - 60 + dy*p, p, p))
    pygame.draw.rect(screen, SKIN, (int(x) + 4*p, ground_y - 60 + 7*p, p, p))
    
    for dy in range(8, 13):
        lx = int(x) - 2*p + int(leg)*p
        pygame.draw.rect(screen, pants, (lx, ground_y - 60 + dy*p, p, p))
    for dy in range(8, 13):
        rx = int(x) + 2*p - int(leg)*p
        pygame.draw.rect(screen, pants, (rx, ground_y - 60 + dy*p, p, p))
    
    pygame.draw.rect(screen, BOOT, (int(x) - 2*p + int(leg)*p, ground_y - 60 + 13*p, 2*p, p))
    pygame.draw.rect(screen, BOOT, (int(x) + 2*p - int(leg)*p, ground_y - 60 + 13*p, 2*p, p))

def draw_chatbox(screen, messages, input_text, input_active, chat_scroll_y):
    chat_x = 250; chat_y = 100; chat_w = SCREEN_W - 500; chat_h = SCREEN_H - 200
    
    s = pygame.Surface((chat_w, chat_h), pygame.SRCALPHA)
    s.fill(CHAT_BG)
    screen.blit(s, (chat_x, chat_y))
    
    pygame.draw.rect(screen, CHAT_BORDER, (chat_x, chat_y, chat_w, chat_h), 3)
    
    close_btn = pygame.Rect(chat_x + chat_w - 40, chat_y + 8, 30, 30)
    pygame.draw.rect(screen, (180, 50, 50), close_btn)
    pygame.draw.rect(screen, (255, 100, 100), close_btn, 2)
    screen.blit(FONT_BTN.render("X", True, WHITE), (close_btn.x + 7, close_btn.y + 2))
    
    title = FONT_BTN.render("Chat com LOKI", True, GOLD)
    screen.blit(title, (chat_x + 20, chat_y + 10))
    
    y_off = chat_y + 50 + chat_scroll_y
    for msg in messages:
        color = WHITE if msg["role"] == "user" else GOLD
        prefix = "Voce: " if msg["role"] == "user" else "LOKI: "
        text = prefix + msg["content"]
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + word + " "
            if FONT_CHAT.size(test)[0] > chat_w - 60:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test
        lines.append(current_line)
        
        for line in lines:
            if y_off > chat_y + 40 and y_off < chat_y + chat_h - 60:
                screen.blit(FONT_CHAT.render(line, True, color), (chat_x + 20, y_off))
            y_off += 25
    
    inp_y = chat_y + chat_h - 50
    pygame.draw.rect(screen, CHAT_INPUT_BG, (chat_x + 15, inp_y, chat_w - 90, 35))
    pygame.draw.rect(screen, (150, 150, 200) if input_active else (100, 100, 150), (chat_x + 15, inp_y, chat_w - 90, 35), 2)
    screen.blit(FONT_CHAT.render(input_text + ("|" if input_active else ""), True, WHITE), (chat_x + 25, inp_y + 7))
    
    send_btn = pygame.Rect(chat_x + chat_w - 65, inp_y, 45, 35)
    pygame.draw.rect(screen, DARK_GREEN, send_btn)
    pygame.draw.rect(screen, (100, 200, 100), send_btn, 2)
    screen.blit(FONT_CHAT.render(">", True, WHITE), (send_btn.x + 15, send_btn.y + 7))
    
    return send_btn, close_btn

def draw_room(screen, andar_idx, floors, chat_messages, chat_input, chat_active, chat_scroll):
    s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    s.fill((20, 20, 40, 200))
    screen.blit(s, (0, 0))
    
    rx = 100; ry = 80; rw = SCREEN_W - 200; rh = SCREEN_H - 160
    pygame.draw.rect(screen, (40, 40, 60), (rx, ry, rw, rh))
    pygame.draw.rect(screen, GOLD, (rx, ry, rw, rh), 3)
    
    # Titulo
    floor_name = f"Andar {andar_idx + 1}"
    if andar_idx < len(floors) and isinstance(floors[andar_idx], dict):
        floor_name = floors[andar_idx].get("nome", floor_name)
    
    title = FONT_BTN.render(f"Sala: {floor_name}", True, GOLD)
    screen.blit(title, (rx + 20, ry + 15))
    
    # Botao voltar
    back_btn = pygame.Rect(rx + 30, ry + rh - 60, 150, 40)
    pygame.draw.rect(screen, (150, 50, 50), back_btn)
    pygame.draw.rect(screen, (255, 100, 100), back_btn, 2)
    screen.blit(FONT_BTN.render("< Voltar", True, WHITE), (back_btn.x + 20, back_btn.y + 8))
    
    # Area do agente
    agent_x = rx + rw // 2 - 30
    agent_y = ry + rh // 2
    for dx in range(-3, 4):
        for dy in range(-5, 0):
            pygame.draw.rect(screen, (101, 55, 0), (agent_x + dx*3, agent_y + dy*3, 3, 3))
    for dx in range(-2, 3):
        for dy in range(-3, 0):
            pygame.draw.rect(screen, SKIN, (agent_x + dx*3, agent_y + dy*3, 3, 3))
    pygame.draw.rect(screen, BLUE_EYE, (agent_x - 3, agent_y - 6, 3, 3))
    pygame.draw.rect(screen, BLUE_EYE, (agent_x + 3, agent_y - 6, 3, 3))
    for dx in range(-3, 4):
        for dy in range(0, 6):
            pygame.draw.rect(screen, (85, 107, 47), (agent_x + dx*3, agent_y + dy*3, 3, 3))
    
    screen.blit(FONT_SM.render("Agente", True, (200, 200, 255)), (agent_x - 30, agent_y + 25))
    
    # Chat
    cx = rx + 20; cy = ry + 60; cw = rw - 40; ch = rh - 150
    
    y_off = cy + chat_scroll
    for msg in chat_messages:
        color = WHITE if msg["role"] == "user" else GOLD
        prefix = "Voce: " if msg["role"] == "user" else "Agente: "
        text = prefix + msg["content"]
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + word + " "
            if FONT_CHAT.size(test)[0] > cw - 40:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test
        lines.append(current_line)
        
        for line in lines:
            if y_off > cy - 20 and y_off < cy + ch - 30:
                screen.blit(FONT_CHAT.render(line, True, color), (cx + 10, y_off))
            y_off += 22
    
    inp_y = cy + ch - 30
    pygame.draw.rect(screen, CHAT_INPUT_BG, (cx + 10, inp_y, cw - 70, 30))
    pygame.draw.rect(screen, (150, 150, 200) if chat_active else (100, 100, 150), (cx + 10, inp_y, cw - 70, 30), 2)
    screen.blit(FONT_CHAT.render(chat_input + ("|" if chat_active else ""), True, WHITE), (cx + 20, inp_y + 5))
    
    send_btn = pygame.Rect(cx + cw - 55, inp_y, 40, 30)
    pygame.draw.rect(screen, DARK_GREEN, send_btn)
    pygame.draw.rect(screen, (100, 200, 100), send_btn, 2)
    screen.blit(FONT_CHAT.render(">", True, WHITE), (send_btn.x + 12, send_btn.y + 5))
    
    return back_btn, send_btn

def draw_create_dialog(screen, available_floors, selected_idx, input_text, input_active, dialog_scroll):
    s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))
    
    win_w, win_h = 600, 500
    win_x = (SCREEN_W - win_w) // 2
    win_y = (SCREEN_H - win_h) // 2
    
    pygame.draw.rect(screen, (40, 40, 60), (win_x, win_y, win_w, win_h))
    pygame.draw.rect(screen, GOLD, (win_x, win_y, win_w, win_h), 3)
    
    title = FONT_BTN.render("Criar Novo Andar", True, GOLD)
    screen.blit(title, (win_x + 20, win_y + 15))
    
    close_btn = pygame.Rect(win_x + win_w - 40, win_y + 10, 30, 30)
    pygame.draw.rect(screen, (180, 50, 50), close_btn)
    pygame.draw.rect(screen, (255, 100, 100), close_btn, 2)
    screen.blit(FONT_BTN.render("X", True, WHITE), (close_btn.x + 7, close_btn.y + 2))
    
    screen.blit(FONT_SM.render("Nome do Andar:", True, WHITE), (win_x + 20, win_y + 60))
    
    input_rect = pygame.Rect(win_x + 20, win_y + 85, win_w - 40, 35)
    pygame.draw.rect(screen, (60, 60, 90), input_rect)
    pygame.draw.rect(screen, (150, 150, 200) if input_active else (100, 100, 150), input_rect, 2)
    input_surf = FONT_SM.render(input_text + ("|" if input_active else ""), True, WHITE)
    screen.blit(input_surf, (win_x + 30, win_y + 92))
    
    screen.blit(FONT_SM.render("Estilo do Andar:", True, WHITE), (win_x + 20, win_y + 135))
    
    grid_area = pygame.Rect(win_x + 20, win_y + 160, win_w - 40, win_h - 240)
    
    cols = 3; btn_w = 170; btn_h = 90
    start_x = grid_area.x; start_y = grid_area.y + dialog_scroll
    style_rects = []
    
    for i, floor_img in enumerate(available_floors):
        col = i % cols; row = i // cols
        bx = start_x + col * (btn_w + 10); by = start_y + row * (btn_h + 15)
        
        if grid_area.y <= by < grid_area.y + grid_area.h and by + btn_h > grid_area.y:
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            style_rects.append((i, rect))
            
            if i == selected_idx:
                pygame.draw.rect(screen, GOLD, (bx - 3, by - 3, btn_w + 6, btn_h + 6))
            
            preview = pygame.transform.scale(floor_img, (btn_w, btn_h - 20))
            screen.blit(preview, (bx, by))
            pygame.draw.rect(screen, (150, 150, 150), (bx, by, btn_w, btn_h - 20), 2)
            
            style_name = STYLE_NAMES.get(i, f"Estilo {i + 1}")
            name_surf = FONT_SM.render(style_name, True, WHITE)
            screen.blit(name_surf, (bx + btn_w // 2 - name_surf.get_width() // 2, by + btn_h - 18))
    
    criar_btn = pygame.Rect(win_x + win_w // 2 - 75, win_y + win_h - 60, 150, 40)
    pygame.draw.rect(screen, DARK_GREEN, criar_btn)
    pygame.draw.rect(screen, (100, 200, 100), criar_btn, 2)
    criar_text = FONT_BTN.render("CRIAR", True, WHITE)
    screen.blit(criar_text, (criar_btn.x + 30, criar_btn.y + 8))
    
    return close_btn, input_rect, style_rects, criar_btn

def main():
    frame = 0
    running = True
    scroll_y = 0
    
    floor_sprites, construction = load_floor_sprites()
    if not floor_sprites:
        print("ERRO: Nenhum andar encontrado!")
        sys.exit(1)
    
    print(f"Total: {len(floor_sprites)} andares carregados")
    
    building_floors = []
    
    npc_data = [
        {"x": 100, "dir": 1, "speed": 1.5, "off": 0, "hair": (101,55,0), "tunic": (85,107,47), "pants": (101,67,33)},
        {"x": 400, "dir": -1, "speed": 1.0, "off": 20, "hair": (50,30,10), "tunic": (60,80,150), "pants": (50,50,80)},
        {"x": 700, "dir": 1, "speed": 1.2, "off": 40, "hair": (180,100,50), "tunic": (150,50,50), "pants": (80,50,30)},
        {"x": 900, "dir": -1, "speed": 0.8, "off": 60, "hair": (200,180,120), "tunic": (100,50,150), "pants": (60,40,80)},
    ]
    
    ground_y = SCREEN_H - 100
    
    create_dialog_open = False
    create_selected_idx = 0
    create_input_text = ""
    create_input_active = False
    create_close_btn = None
    create_input_rect = None
    create_style_rects = []
    create_criar_btn = None
    dialog_scroll = 0
    
    chat_open = False
    chat_messages = []
    chat_input = ""
    chat_input_active = False
    chat_send_btn = None
    chat_close_btn = None
    chat_is_sending = False
    chat_scroll_y = 0
    
    sala_open = False
    sala_atual = 0
    chat_messages_room = []
    chat_input_room = ""
    chat_active_room = False
    chat_scroll_room = 0
    back_btn_room = None
    chat_send_btn_room = None
    
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
                    
                    if create_dialog_open:
                        if create_close_btn and create_close_btn.collidepoint(mouse_pos):
                            create_dialog_open = False
                        if create_input_rect and create_input_rect.collidepoint(mouse_pos):
                            create_input_active = True
                        else:
                            create_input_active = False
                        for i, rect in create_style_rects:
                            if rect.collidepoint(mouse_pos):
                                create_selected_idx = i
                        if create_criar_btn and create_criar_btn.collidepoint(mouse_pos):
                            if create_input_text.strip() and create_selected_idx < len(floor_sprites):
                                new_floor = {
                                    "sprite": floor_sprites[create_selected_idx],
                                    "nome": create_input_text.strip(),
                                    "projeto": "Projeto em decorrencia"
                                }
                                building_floors.append(new_floor)
                                create_dialog_open = False
                                create_input_text = ""
                                # Abre sala do novo andar
                                sala_atual = len(building_floors) - 1
                                sala_open = True
                                chat_messages_room = []
                                chat_input_room = ""
                                chat_active_room = True
                    elif sala_open:
                        if back_btn_room and back_btn_room.collidepoint(mouse_pos):
                            sala_open = False
                        if chat_send_btn_room and chat_send_btn_room.collidepoint(mouse_pos):
                            if chat_input_room.strip():
                                chat_messages_room.append({"role": "user", "content": chat_input_room})
                                chat_input_room = ""
                                # Envia para IA
                                ctx_msg = [{"role": "system", "content": f"Voce eh o agente do projeto '{new_floor.get('nome', 'Projeto')}' no predio LOKI em Aveiro. Ajude o visitante."}] + chat_messages_room[-5:]
                                thread = threading.Thread(target=lambda c=ctx_msg, m=chat_messages_room, b=list(building_floors): chat_async(c, m, b))
                                thread.daemon = True
                                thread.start()
                    elif chat_open:
                        if chat_close_btn and chat_close_btn.collidepoint(mouse_pos):
                            chat_open = False
                        if chat_send_btn and chat_send_btn.collidepoint(mouse_pos):
                            if chat_input.strip() and not chat_is_sending:
                                chat_messages.append({"role": "user", "content": chat_input})
                                chat_input = ""
                                chat_is_sending = True
                    else:
                        # Verifica clique no LOKI
                        loki_rect = pygame.Rect(loki_x - 30, sidewalk_y - 60, 60, 100)
                        if loki_rect.collidepoint(mouse_pos):
                            chat_open = True
                            chat_input_active = True
                        else:
                            # Clique no predio - abrir sala
                            building_rect = pygame.Rect(bx, 0, BUILDING_W, SCREEN_H)
                            if building_rect.collidepoint(mouse_pos) and building_floors:
                                sala_atual = len(building_floors) - 1
                                sala_open = True
                                chat_messages_room = []
                                chat_input_room = ""
                                chat_active_room = True
                
                elif event.button == 4:
                    if create_dialog_open:
                        dialog_scroll = min(0, dialog_scroll + 40)
                    elif sala_open:
                        chat_scroll_room = min(0, chat_scroll_room + 30)
                    elif chat_open:
                        chat_scroll_y = min(0, chat_scroll_y + 30)
                    else:
                        scroll_y = min(scroll_y + 80, max(0, sum(f.get("sprite", f).get_height() if isinstance(f, dict) else f.get_height() for f in building_floors) + 450 - SCREEN_H))
                elif event.button == 5:
                    if create_dialog_open:
                        dialog_scroll = max(-200, dialog_scroll - 40)
                    elif sala_open:
                        chat_scroll_room = max(-500, chat_scroll_room - 30)
                    elif chat_open:
                        chat_scroll_y = max(-500, chat_scroll_y - 30)
                    else:
                        scroll_y = max(0, scroll_y - 80)
            
            if event.type == pygame.KEYDOWN:
                if create_dialog_open:
                    if event.key == pygame.K_BACKSPACE:
                        create_input_text = create_input_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        create_dialog_open = False
                    elif event.unicode and event.key < 256:
                        create_input_text += event.unicode
                elif sala_open:
                    if event.key == pygame.K_BACKSPACE:
                        chat_input_room = chat_input_room[:-1]
                    elif event.key == pygame.K_RETURN:
                        if chat_input_room.strip():
                            chat_messages_room.append({"role": "user", "content": chat_input_room})
                            chat_input_room = ""
                            # Envia para IA
                            floor_name = f"Andar {sala_atual + 1}"
                            if sala_atual < len(building_floors) and isinstance(building_floors[sala_atual], dict):
                                floor_name = building_floors[sala_atual].get("nome", floor_name)
                            ctx_msg = [{"role": "system", "content": f"Voce eh o agente do projeto '{floor_name}' no predio LOKI em Aveiro. Ajude o visitante com informacoes sobre este projeto."}] + chat_messages_room[-5:]
                            thread = threading.Thread(target=lambda c=ctx_msg, m=chat_messages_room, b=list(building_floors): chat_async(c, m, b))
                            thread.daemon = True
                            thread.start()
                    elif event.key == pygame.K_ESCAPE:
                        sala_open = False
                    elif event.unicode and event.key < 256 and chat_active_room:
                        chat_input_room += event.unicode
                elif chat_open:
                    if event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        if chat_input.strip() and not chat_is_sending:
                            chat_messages.append({"role": "user", "content": chat_input})
                            chat_input = ""
                            chat_is_sending = True
                    elif event.key == pygame.K_ESCAPE:
                        chat_open = False
                    elif event.unicode and event.key < 256:
                        chat_input += event.unicode
        
        current_hour = time.localtime().tm_hour
        draw_sky(screen, current_hour)
        
        # Chao
        pygame.draw.rect(screen, (60,60,60), (0, ground_y, SCREEN_W, 100))
        pygame.draw.rect(screen, (40,40,40), (0, ground_y+40, SCREEN_W, 60))
        for fx in range(0, SCREEN_W, 60):
            pygame.draw.rect(screen, (200,200,100), (fx, ground_y+65, 30, 6))
        
        # Predio
        bx = (SCREEN_W - BUILDING_W) // 2
        current_y = ground_y
        
        if not building_floors and construction:
            h = construction.get_height()
            screen.blit(construction, (bx, current_y - h))
            # Placa
            sign_x = bx - 140; sign_y = current_y - h + 20
            pygame.draw.rect(screen, (150,100,0), (sign_x, sign_y, 120, 50))
            pygame.draw.rect(screen, WHITE, (sign_x, sign_y, 120, 50), 2)
            t1 = FONT_SM.render("Em", True, WHITE)
            t2 = FONT_SM.render("Construcao", True, WHITE)
            screen.blit(t1, (sign_x + 60 - t1.get_width()//2, sign_y + 8))
            screen.blit(t2, (sign_x + 60 - t2.get_width()//2, sign_y + 28))
        else:
            for i, floor in enumerate(building_floors):
                if isinstance(floor, dict):
                    img = floor["sprite"]; nome = floor.get("nome", "")
                else:
                    img = floor; nome = ""
                
                h = img.get_height()
                screen.blit(img, (bx, current_y - h))
                
                if nome:
                    sign_x = bx - 140; sign_y = current_y - h + 20
                    pygame.draw.rect(screen, (0,150,0), (sign_x, sign_y, 120, 35))
                    pygame.draw.rect(screen, WHITE, (sign_x, sign_y, 120, 35), 2)
                    display_nome = nome[:12] + "..." if len(nome) > 12 else nome
                    text_surf = FONT_SM.render(display_nome, True, WHITE)
                    text_rect = text_surf.get_rect(center=(sign_x + 60, sign_y + 17))
                    screen.blit(text_surf, text_rect)
                
                current_y -= h
        
        # NPCs na calcada
        sidewalk_y = ground_y - 20
        for npc in npc_data:
            npc["x"] += npc["speed"] * npc["dir"]
            if npc["x"] > SCREEN_W - 100:
                npc["dir"] = -1
            elif npc["x"] < 50:
                npc["dir"] = 1
            
            draw_npc_walking(screen, npc["x"], sidewalk_y, frame, npc["off"], npc["hair"], npc["tunic"], npc["pants"])
        
        # NPC LOKI (agente principal ao lado do predio)
        loki_x = bx - 80
        # LOKI com cores especiais (dourado)
        for dx in range(-4, 5):
            for dy in range(-6, 0):
                if abs(dx) <= 3 and dy >= -5:
                    pygame.draw.rect(screen, (180, 150, 50), (loki_x + dx*3, sidewalk_y - 60 + dy*3, 3, 3))
        for dx in range(-5, 6):
            for dy in range(-4, 2):
                if abs(dx) >= 3 and abs(dx) <= 4:
                    pygame.draw.rect(screen, (180, 150, 50), (loki_x + dx*3, sidewalk_y - 60 + dy*3, 3, 3))
        for dx in range(-3, 4):
            for dy in range(-4, 2):
                if abs(dx) <= 2 and dy >= -3:
                    pygame.draw.rect(screen, SKIN, (loki_x + dx*3, sidewalk_y - 60 + dy*3, 3, 3))
        pygame.draw.rect(screen, (255, 200, 50), (loki_x - 3, sidewalk_y - 60 - 6, 3, 3))
        pygame.draw.rect(screen, (255, 200, 50), (loki_x + 3, sidewalk_y - 60 - 6, 3, 3))
        for dx in range(-3, 4):
            for dy in range(2, 8):
                pygame.draw.rect(screen, (200, 150, 50), (loki_x + dx*3, sidewalk_y - 60 + dy*3, 3, 3))
        for dx in range(-3, 4):
            pygame.draw.rect(screen, GOLD, (loki_x + dx*3, sidewalk_y - 60 + 21, 3, 3))
        pygame.draw.rect(screen, GOLD, (loki_x - 3, sidewalk_y - 60 + 21, 6, 3))
        for dy in range(3, 7):
            pygame.draw.rect(screen, (200, 150, 50), (loki_x - 12, sidewalk_y - 60 + dy*3, 3, 3))
        pygame.draw.rect(screen, SKIN, (loki_x - 12, sidewalk_y - 60 + 21, 3, 3))
        for dy in range(3, 7):
            pygame.draw.rect(screen, (200, 150, 50), (loki_x + 12, sidewalk_y - 60 + dy*3, 3, 3))
        pygame.draw.rect(screen, SKIN, (loki_x + 12, sidewalk_y - 60 + 21, 3, 3))
        for dy in range(8, 13):
            pygame.draw.rect(screen, (100, 77, 0), (loki_x - 6, sidewalk_y - 60 + dy*3, 3, 3))
            pygame.draw.rect(screen, (100, 77, 0), (loki_x + 6, sidewalk_y - 60 + dy*3, 3, 3))
        pygame.draw.rect(screen, BOOT, (loki_x - 6, sidewalk_y - 60 + 39, 6, 3))
        pygame.draw.rect(screen, BOOT, (loki_x + 6, sidewalk_y - 60 + 39, 6, 3))
        screen.blit(FONT_SM.render("LOKI", True, GOLD), (loki_x - 25, sidewalk_y + 25))
        
        # UI
        title = FONT_TITLE.render("LOKI", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 35)))
        
        sub = FONT_SUB.render("LIFE OS", True, WHITE)
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 80)))
        
        screen.blit(FONT_SM.render(f"Andares: {len(building_floors)}", True, WHITE), (10, 10))
        screen.blit(FONT_SM.render(f"{current_hour}:00", True, WHITE), (10, 35))
        
        add_w = FONT_BTN.render("ADICIONAR ANDAR", True, WHITE).get_width() + 48
        add_h = FONT_BTN.render("ADICIONAR ANDAR", True, WHITE).get_height() + 24
        enter_w = FONT_BTN.render("ENTER", True, WHITE).get_width() + 48
        enter_h = FONT_BTN.render("ENTER", True, WHITE).get_height() + 24
        
        btn_x = SCREEN_W - max(add_w, enter_w) - 30
        
        btn_add = pygame.Rect(btn_x, SCREEN_H // 2 - 60, add_w, add_h)
        pygame.draw.rect(screen, DARK_GREEN, btn_add)
        pygame.draw.rect(screen, (100, 200, 100), btn_add, 2)
        add_text = FONT_BTN.render("ADICIONAR ANDAR", True, WHITE)
        screen.blit(add_text, add_text.get_rect(center=btn_add.center))
        
        btn_enter = pygame.Rect(btn_x, SCREEN_H // 2 + 10, enter_w, enter_h)
        pygame.draw.rect(screen, (50, 80, 150), btn_enter)
        pygame.draw.rect(screen, (100, 150, 200), btn_enter, 2)
        enter_text = FONT_BTN.render("ENTER", True, WHITE)
        screen.blit(enter_text, enter_text.get_rect(center=btn_enter.center))
        
        if clicked:
            if btn_add.collidepoint(mouse_pos):
                create_dialog_open = True
                create_selected_idx = 0
                create_input_text = ""
                dialog_scroll = 0
        
        # Create dialog
        if create_dialog_open:
            result = draw_create_dialog(screen, floor_sprites, create_selected_idx, create_input_text, create_input_active, dialog_scroll)
            create_close_btn = result[0]
            create_input_rect = result[1]
            create_style_rects = result[2]
            create_criar_btn = result[3]
        
        # Process main chat
        if chat_is_sending and len(chat_messages) > 0 and chat_messages[-1]["role"] == "user":
            context = chat_messages[-5:]
            chat_messages.append({"role": "assistant", "content": "Aguarde..."})
            thread = threading.Thread(target=lambda c=context, m=chat_messages, b=list(building_floors): chat_async(c, m, b))
            thread.daemon = True
            thread.start()
            chat_is_sending = False
        
        # Chatbox (NPC)
        if chat_open:
            chat_send_btn, chat_close_btn = draw_chatbox(screen, chat_messages, chat_input, chat_input_active, chat_scroll_y)
        
        # Room view
        if sala_open:
            back_btn_room, chat_send_btn_room = draw_room(screen, sala_atual, building_floors, chat_messages_room, chat_input_room, chat_active_room, chat_scroll_room)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
