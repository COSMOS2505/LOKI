"""
LOKI - Tela de Introducao (Parte 1)
====================================
Andares em pixel-art, scroll, NPCs no chao, ciclo dia/noite.
NPC com chatbox IA (LLAMA) quando clicado.
"""

import pygame
import sys
import time
import math
import random
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
SKIN=(255,218,185); HAIR=(101,55,0); BLUE_EYE=(50,100,200); TUNIC=(85,107,47)
TUNIC_BELT=(60,80,30); PANTS=(101,67,33); BOOT=(30,20,10)
RED=(200,50,50); DARK_RED=(139,0,0); GREEN_FLAG=(34,100,34)
STONE=(150,150,150); DARK_STONE=(100,100,100); DARKER_STONE=(70,70,70)
WOOD=(101,67,33); DARK_WOOD=(60,40,20); DARKER_WOOD=(40,25,10)
BEIGE=(230,210,170); PLASTE=(210,190,150); WINDOW_LIT=(255,220,100)
WINDOW_DAY=(135,206,235); ROOF=(50,50,70); ROOF_DARK=(35,35,50)
BROWN_BRICK=(139,90,43); TAN=(210,180,140); DARK_BROWN=(80,50,20)
CHAT_BG = (30, 30, 50, 230)
CHAT_BORDER = (100, 100, 150)
CHAT_INPUT_BG = (50, 50, 80)

# ═══════════════════════════════════════════════════════════════════════
# CHAT COM IA (LLAMA)
# ═══════════════════════════════════════════════════════════════════════

def chat_with_ia(messages, model="qwen2.5:1.5b"):
    """Envia mensagem para o Ollama local e retorna a resposta."""
    try:
        url = "http://localhost:11434/api/chat"
        
        # System prompt fixo - Síndico do prédio em Aveiro
        system_prompt = {
            "role": "system", 
            "content": """Você é o SÍNDICO do prédio LOKI, localizado em Aveiro, Portugal.

INFORMAÇÕES REAIS DO PRÉDIO:
- Nome: LOKI
- Localização: Aveiro, Portugal
- Cada andar representa um PROJETO EM DECORRÊNCIA (andares em construção/atividade)
- Você é o síndico responsável por gerir o prédio e ajudar os visitantes

REGRAS IMPORTANTES:
1. NUNCA invente informações (nomes de arquitetos, datas, fatos históricos)
2. Se não souber algo, diga "Não tenho essa informação no momento"
3. Fale apenas sobre o prédio LOKI em Aveiro e seus projetos
4. Seja prestativo, profissional e conciso
5. Responda sempre em português de Portugal

Seu papel: Ajudar visitantes com informações sobre o prédio, seus projetos em decorrência, e resolver dúvidas sobre o funcionamento do edifício."""
        }
        
        # Adiciona system prompt no início
        full_messages = [system_prompt] + [m for m in messages if m["role"] != "system"]
        
        payload = {
            "model": model,
            "messages": full_messages,
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "num_gpu": 0  # CPU only
            }
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["message"]["content"]
    
    except urllib.error.URLError:
        return "[Erro: Ollama não está rodando. Inicie com: ollama serve]"
    except Exception as e:
        return f"[Erro: {str(e)}]"


def chat_async(messages, chat_messages):
    """Envia mensagem em background e atualiza o chat."""
    try:
        resposta = chat_with_ia(messages)
        # Substitui "Aguarde..." pela resposta real
        for i in range(len(chat_messages) - 1, -1, -1):
            if chat_messages[i]["content"] == "Aguarde...":
                chat_messages[i]["content"] = resposta
                break
    except Exception as e:
        for i in range(len(chat_messages) - 1, -1, -1):
            if chat_messages[i]["content"] == "Aguarde...":
                chat_messages[i]["content"] = f"[Erro: {str(e)}]"
                break

# ═══════════════════════════════════════════════════════════════════════
# CICLO DIA/NOITE
# ═══════════════════════════════════════════════════════════════════════

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
    """Carrega todos os andar_*.png da pasta assets/ e escala para BUILDING_W."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_path, "assets")
    files = sorted(glob.glob(os.path.join(asset_path, "andar_*.png")))
    
    sprites = []
    for f in files:
        img = pygame.image.load(f).convert_alpha()
        w, h = img.get_size()
        scale = BUILDING_W / w
        new_h = int(h * scale)
        img_scaled = pygame.transform.scale(img, (BUILDING_W, new_h))
        sprites.append(img_scaled)
        print(f"  Carregado: {os.path.basename(f)} ({w}x{h} -> {BUILDING_W}x{new_h})")
    
    return sprites

def world_to_screen(y, scroll_y):
    return y + scroll_y

def calculate_total_height(floors, overlap_ratio=0.12):
    if not floors:
        return 0
    total = floors[0].get_height()
    for i in range(1, len(floors)):
        h = floors[i].get_height()
        prev_h = floors[i-1].get_height()
        overlap = int(prev_h * overlap_ratio)
        total += h - overlap
    return total

# ═══════════════════════════════════════════════════════════════════════
# NPC PARADO
# ═══════════════════════════════════════════════════════════════════════

class NPC:
    """NPC parado que pode ser clicado para abrir chat."""
    
    def __init__(self, x, y, name="Guardião"):
        self.x = x
        self.y = y
        self.name = name
        self.width = 30
        self.height = 60
        self.hovered = False
        self.pulse = 0
    
    def draw(self, screen):
        # Hitbox (para debug, remover depois)
        # pygame.draw.rect(screen, (255,0,0), (self.x-15, self.y-60, 30, 60), 1)
        
        # Pulso quando hover
        if self.hovered:
            self.pulse = (self.pulse + 0.1) % (math.pi * 2)
            glow = int(abs(math.sin(self.pulse)) * 15)
            pygame.draw.circle(screen, (100+glow, 150+glow, 255), (self.x, self.y-30), 35, 3)
        
        # Sprite do NPC (estático)
        p = 3
        # Cabelo
        for dx in range(-4,5):
            for dy in range(-6,0):
                if abs(dx)<=3 and dy>=-5:
                    pygame.draw.rect(screen, HAIR, (self.x+dx*p, self.y-60+dy*p, p, p))
        for dx in range(-5,6):
            for dy in range(-4,2):
                if abs(dx)>=3 and abs(dx)<=4:
                    pygame.draw.rect(screen, HAIR, (self.x+dx*p, self.y-60+dy*p, p, p))
        # Pele
        for dx in range(-3,4):
            for dy in range(-4,2):
                if abs(dx)<=2 and dy>=-3:
                    pygame.draw.rect(screen, SKIN, (self.x+dx*p, self.y-60+dy*p, p, p))
        # Olhos
        pygame.draw.rect(screen, BLUE_EYE, (self.x-1*p, self.y-60-2*p, p, p))
        pygame.draw.rect(screen, BLUE_EYE, (self.x+1*p, self.y-60-2*p, p, p))
        # Túnica
        for dx in range(-3,4):
            for dy in range(2,8):
                pygame.draw.rect(screen, TUNIC, (self.x+dx*p, self.y-60+dy*p, p, p))
        # Cinto
        for dx in range(-3,4):
            pygame.draw.rect(screen, TUNIC_BELT, (self.x+dx*p, self.y-60+7*p, p, p))
        pygame.draw.rect(screen, GOLD, (self.x-1*p, self.y-60+7*p, 2*p, p))
        # Braços
        for dy in range(3,7):
            pygame.draw.rect(screen, TUNIC, (self.x-4*p, self.y-60+dy*p, p, p))
        pygame.draw.rect(screen, SKIN, (self.x-4*p, self.y-60+7*p, p, p))
        for dy in range(3,7):
            pygame.draw.rect(screen, TUNIC, (self.x+4*p, self.y-60+dy*p, p, p))
        pygame.draw.rect(screen, SKIN, (self.x+4*p, self.y-60+7*p, p, p))
        # Pernas
        for dy in range(8,13):
            pygame.draw.rect(screen, PANTS, (self.x-2*p, self.y-60+dy*p, p, p))
        for dy in range(8,13):
            pygame.draw.rect(screen, PANTS, (self.x+2*p, self.y-60+dy*p, p, p))
        # Botas
        pygame.draw.rect(screen, BOOT, (self.x-2*p, self.y-60+13*p, 2*p, p))
        pygame.draw.rect(screen, BOOT, (self.x+2*p, self.y-60+13*p, 2*p, p))
    
    def check_hover(self, mouse_pos):
        self.hovered = (self.x - 15 <= mouse_pos[0] <= self.x + 15 and
                       self.y - 60 <= mouse_pos[1] <= self.y)
        return self.hovered
    
    def check_click(self, mouse_pos):
        return self.check_hover(mouse_pos)

# ═══════════════════════════════════════════════════════════════════════
# CHATBOX
# ═══════════════════════════════════════════════════════════════════════

def draw_chatbox(screen, messages, input_text, input_active, scroll_y_world, chat_scroll_y):
    """Desenha a chatbox de conversa com IA."""
    # Dimensões da chatbox
    chat_x = 250
    chat_y = 100
    chat_w = SCREEN_W - 500
    chat_h = SCREEN_H - 250
    
    # Fundo semi-transparente
    s = pygame.Surface((chat_w, chat_h), pygame.SRCALPHA)
    s.fill(CHAT_BG)
    screen.blit(s, (chat_x, chat_y))
    
    # Borda
    pygame.draw.rect(screen, CHAT_BORDER, (chat_x, chat_y, chat_w, chat_h), 3)
    
    # Botão fechar (X vermelho)
    close_btn = pygame.Rect(chat_x + chat_w - 40, chat_y + 8, 30, 30)
    pygame.draw.rect(screen, (180, 50, 50), close_btn)
    pygame.draw.rect(screen, (255, 100, 100), close_btn, 2)
    x_text = FONT_BTN.render("X", True, WHITE)
    screen.blit(x_text, (close_btn.x + 7, close_btn.y + 2))
    
    # Título
    title = FONT_BTN.render("Chat com LOKI", True, GOLD)
    screen.blit(title, (chat_x + 20, chat_y + 10))
    
    # Separador
    pygame.draw.line(screen, CHAT_BORDER, (chat_x + 10, chat_y + 45), (chat_x + chat_w - 10, chat_y + 45), 2)
    
    # Área de mensagens (com clipping)
    msg_area_x = chat_x + 20
    msg_area_y = chat_y + 60
    msg_area_w = chat_w - 40
    msg_area_h = chat_h - 120
    msg_area_clip = pygame.Rect(msg_area_x, msg_area_y, msg_area_w, msg_area_h)
    
    # Renderiza mensagens com scroll
    y_offset = msg_area_y + chat_scroll_y
    
    for msg in messages[-50:]:  # Mostra até últimas 50 mensagens
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            color = (100, 200, 255)
            prefix = "Você: "
        elif role == "assistant":
            color = (200, 255, 100)
            prefix = "LOKI: "
        else:
            continue  # Pula system
        
        # Quebra linhas longas
        words = (prefix + content).split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if FONT_CHAT.size(test_line)[0] > msg_area_w - 20:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        lines.append(current_line)
        
        for line in lines:
            if msg_area_y <= y_offset < msg_area_y + msg_area_h - 20:
                text_surf = FONT_CHAT.render(line, True, color)
                screen.blit(text_surf, (msg_area_x + 10, y_offset))
            y_offset += 22
        
        y_offset += 8  # Espaço entre mensagens
    
    # Indicador de scroll
    total_content_height = y_offset - msg_area_y
    if total_content_height > msg_area_h:
        # Mostra indicador de scroll
        scroll_indicator_h = max(30, int(msg_area_h * (msg_area_h / total_content_height)))
        scroll_pos = int((chat_scroll_y / (total_content_height - msg_area_h)) * (msg_area_h - scroll_indicator_h))
        pygame.draw.rect(screen, (80, 80, 120), (chat_x + chat_w - 15, msg_area_y + scroll_pos, 8, scroll_indicator_h))
    
    # Campo de input
    input_y = chat_y + chat_h - 60
    pygame.draw.rect(screen, CHAT_INPUT_BG, (chat_x + 20, input_y, chat_w - 100, 40))
    pygame.draw.rect(screen, CHAT_BORDER, (chat_x + 20, input_y, chat_w - 100, 40), 2)
    
    # Texto do input
    input_surf = FONT_CHAT.render(input_text + ("|" if input_active else ""), True, WHITE)
    screen.blit(input_surf, (chat_x + 30, input_y + 10))
    
    # Botão de enviar
    send_btn = pygame.Rect(chat_x + chat_w - 70, input_y, 50, 40)
    pygame.draw.rect(screen, DARK_GREEN, send_btn)
    pygame.draw.rect(screen, (100,200,100), send_btn, 2)
    send_text = FONT_CHAT.render(">", True, WHITE)
    screen.blit(send_text, (send_btn.x + 18, send_btn.y + 10))
    
    # Instrução
    instr = FONT_SM.render("ESC para fechar | Scroll para navegar", True, (150,150,150))
    screen.blit(instr, (chat_x + 20, chat_y + chat_h - 90))
    
    return send_btn, close_btn

# ═══════════════════════════════════════════════════════════════════════
# EDIFÍCIO
# ═══════════════════════════════════════════════════════════════════════

def draw_building(screen, floors, hour, frame, scroll_y, floor_sprites):
    """Desenha o prédio ancorado no chão."""
    total_h = calculate_total_height(floors)
    bx = (SCREEN_W - BUILDING_W) // 2
    
    # Coordenadas do mundo
    ground_y = SCREEN_H - 120
    floor_base_y = ground_y
    
    # --- CHAO ---
    sy = world_to_screen(ground_y, scroll_y)
    pygame.draw.rect(screen, (100,100,100), (0, sy, SCREEN_W, 120))
    pygame.draw.rect(screen, (60,60,60), (0, sy+50, SCREEN_W, 70))
    for fx in range(0, SCREEN_W, 60):
        pygame.draw.rect(screen, (200,200,100), (fx, sy+80, 30, 6))
    
    # --- ANDARES (cresce para cima) ---
    current_y = floor_base_y  # posição da base do andar atual
    for img in floors:
        h = img.get_height()
        screen_y = current_y - h + scroll_y  # desenha o andar acima da posição atual
        screen.blit(img, (bx, screen_y))
        current_y -= h  # próximo andar fica acima deste
    
    return ground_y

# ═══════════════════════════════════════════════════════════════════════
# BOTAO
# ═══════════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    frame = 0
    running = True
    entering = False
    enter_timer = 60
    scroll_y = 0
    
    # Estado do chat
    chat_open = False
    chat_messages = []
    chat_input = ""
    chat_input_active = False
    chat_send_btn = None
    chat_close_btn = None
    chat_is_sending = False
    chat_scroll_y = 0
    
    print("Carregando andares...")
    floor_sprites = load_floor_sprites()
    if not floor_sprites:
        print("ERRO: Nenhum andar encontrado em assets/andar_*.png")
        sys.exit(1)
    
    print(f"Total: {len(floor_sprites)} andares carregados")
    
    building_floors = [random.choice(floor_sprites), random.choice(floor_sprites)]
    
    # NPCs no chão (para andar)
    npc_data = [
        {"x":100, "world_y":SCREEN_H-140, "speed":1.5, "dir":1, "off":0},
        {"x":400, "world_y":SCREEN_H-140, "speed":1.0, "dir":-1, "off":20},
        {"x":700, "world_y":SCREEN_H-140, "speed":1.2, "dir":1, "off":40},
    ]
    
    # NPC parado ao lado do prédio (para chat)
    bx = (SCREEN_W - BUILDING_W) // 2
    npc_chat = NPC(bx - 60, SCREEN_H - 120)
    
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
                    # Verifica clique no NPC de chat
                    if not chat_open and npc_chat.check_click(mouse_pos):
                        chat_open = True
                        chat_input_active = True
                    # Verifica clique no botão de enviar
                    elif chat_open and chat_send_btn and chat_send_btn.collidepoint(mouse_pos):
                        if chat_input.strip() and not chat_is_sending:
                            chat_messages.append({"role": "user", "content": chat_input})
                            chat_input = ""
                            chat_is_sending = True
                    # Verifica clique no botão fechar
                    elif chat_open and chat_close_btn and chat_close_btn.collidepoint(mouse_pos):
                        chat_open = False
                        chat_input_active = False
                elif event.button == 4:
                    if chat_open:
                        chat_scroll_y = min(0, chat_scroll_y + 30)
                    else:
                        scroll_y = min(scroll_y + 80, max(0, calculate_total_height(building_floors) + 3*150 - SCREEN_H + 200))
                elif event.button == 5:
                    if chat_open:
                        chat_scroll_y = max(-500, chat_scroll_y - 30)
                    else:
                        scroll_y = max(0, scroll_y - 80)
            
            if event.type == pygame.KEYDOWN and chat_open:
                if event.key == pygame.K_BACKSPACE:
                    chat_input = chat_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if chat_input.strip() and not chat_is_sending:
                        chat_messages.append({"role": "user", "content": chat_input})
                        chat_input = ""
                        chat_is_sending = True
                elif event.key == pygame.K_ESCAPE:
                    chat_open = False
                    chat_input_active = False
                elif event.unicode and event.key < 256:
                    chat_input += event.unicode
        
        # Atualiza NPC hover
        npc_chat.hovered = npc_chat.check_hover(mouse_pos)
        
        # Processa resposta da IA (em background)
        if chat_is_sending and len(chat_messages) > 0 and chat_messages[-1]["role"] == "user":
            # Pega últimas mensagens para contexto
            context = chat_messages[-5:]
            # Mostra mensagem de aguarde imediatamente
            chat_messages.append({"role": "assistant", "content": "Aguarde..."})
            # Envia em background
            thread = threading.Thread(target=lambda: chat_async(context, chat_messages))
            thread.daemon = True
            thread.start()
            chat_is_sending = False
        
        # Botoes na lateral direita
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
        
        if clicked and hover_add and not entering and not chat_open:
            next_idx = len(building_floors) % len(floor_sprites)
            building_floors.append(floor_sprites[next_idx])
            total_h = len(building_floors) * 150
            max_scroll = max(0, total_h + 3*150 - SCREEN_H + 200)
            scroll_y = max_scroll
        
        if clicked and hover_enter and not entering and not chat_open:
            entering = True
            enter_timer = 60
        if entering:
            enter_timer -= 1
            if enter_timer <= 0:
                print(f"ENTRANDO! Andares: {len(building_floors)}")
                entering = False
        
        current_hour = time.localtime().tm_hour
        
        # Desenho
        draw_sky(screen, current_hour)
        ground_y = draw_building(screen, building_floors, current_hour, frame, scroll_y, floor_sprites)
        
        # NPCs andando
        for npc in npc_data:
            npc["x"] += npc["speed"] * npc["dir"]
            if npc["x"] > SCREEN_W-100: npc["dir"] = -1
            elif npc["x"] < 50: npc["dir"] = 1
            npc_screen_y = world_to_screen(npc["world_y"], scroll_y)
            # Desenhar NPC andando
            p = 3
            for dx in range(-4,5):
                for dy in range(-6,0):
                    if abs(dx)<=3 and dy>=-5:
                        pygame.draw.rect(screen, HAIR, (int(npc["x"])+dx*p, npc_screen_y-60+dy*p, p, p))
            for dx in range(-5,6):
                for dy in range(-4,2):
                    if abs(dx)>=3 and abs(dx)<=4:
                        pygame.draw.rect(screen, HAIR, (int(npc["x"])+dx*p, npc_screen_y-60+dy*p, p, p))
            for dx in range(-3,4):
                for dy in range(-4,2):
                    if abs(dx)<=2 and dy>=-3:
                        pygame.draw.rect(screen, SKIN, (int(npc["x"])+dx*p, npc_screen_y-60+dy*p, p, p))
            pygame.draw.rect(screen, BLUE_EYE, (int(npc["x"])-1*p, npc_screen_y-60-2*p, p, p))
            pygame.draw.rect(screen, BLUE_EYE, (int(npc["x"])+1*p, npc_screen_y-60-2*p, p, p))
            for dx in range(-3,4):
                for dy in range(2,8):
                    pygame.draw.rect(screen, TUNIC, (int(npc["x"])+dx*p, npc_screen_y-60+dy*p, p, p))
            for dx in range(-3,4):
                pygame.draw.rect(screen, TUNIC_BELT, (int(npc["x"])+dx*p, npc_screen_y-60+7*p, p, p))
            pygame.draw.rect(screen, GOLD, (int(npc["x"])-1*p, npc_screen_y-60+7*p, 2*p, p))
            for dy in range(3,7):
                pygame.draw.rect(screen, TUNIC, (int(npc["x"])-4*p, npc_screen_y-60+dy*p, p, p))
            pygame.draw.rect(screen, SKIN, (int(npc["x"])-4*p, npc_screen_y-60+7*p, p, p))
            for dy in range(3,7):
                pygame.draw.rect(screen, TUNIC, (int(npc["x"])+4*p, npc_screen_y-60+dy*p, p, p))
            pygame.draw.rect(screen, SKIN, (int(npc["x"])+4*p, npc_screen_y-60+7*p, p, p))
            leg = math.sin((frame+npc["off"])*0.15)*2
            for dy in range(8,13):
                lx = int(npc["x"])-2*p+int(leg)*p
                pygame.draw.rect(screen, PANTS, (lx, npc_screen_y-60+dy*p, p, p))
            for dy in range(8,13):
                rx = int(npc["x"])+2*p-int(leg)*p
                pygame.draw.rect(screen, PANTS, (rx, npc_screen_y-60+dy*p, p, p))
            pygame.draw.rect(screen, BOOT, (int(npc["x"])-2*p+int(leg)*p, npc_screen_y-60+13*p, 2*p, p))
            pygame.draw.rect(screen, BOOT, (int(npc["x"])+2*p-int(leg)*p, npc_screen_y-60+13*p, 2*p, p))
        
        # NPC de chat (ao lado do prédio)
        npc_chat.y = world_to_screen(SCREEN_H - 120, scroll_y)
        npc_chat.draw(screen)
        
        # HUD
        title = FONT_TITLE.render("LOKI", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_W//2, 35)))
        sub = FONT_SUB.render("LIFE OS", True, WHITE)
        screen.blit(sub, sub.get_rect(center=(SCREEN_W//2, 80)))
        
        screen.blit(FONT_SM.render(f"Andares: {len(building_floors)}", True, WHITE), (10,10))
        screen.blit(FONT_SM.render(f"{current_hour:02d}:00", True, WHITE), (10,30))
        
        # Indica NPC clicável
        if npc_chat.hovered:
            hint = FONT_SM.render("Clique para conversar", True, GOLD)
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 40))
        
        if not chat_open:
            if not entering:
                draw_button(screen, btn_add_x, btn_add_y, "ADICIONAR ANDAR", hover_add, frame, DARK_GREEN)
                draw_button(screen, btn_enter_x, btn_enter_y, "ENTER", hover_enter, frame, (34,85,170))
        else:
            ent = FONT_BTN.render("ENTRANDO...", True, GOLD)
            screen.blit(ent, ent.get_rect(center=(SCREEN_W//2, btn_enter_y+enter_h//2)))
        
        # Chatbox
        if chat_open:
            result = draw_chatbox(screen, chat_messages, chat_input, chat_input_active, scroll_y, chat_scroll_y)
            chat_send_btn = result[0]
            chat_close_btn = result[1]
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
