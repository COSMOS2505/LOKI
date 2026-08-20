# 🏗️ LOKI — Life OS

> Gestor de projetos e planeamento com estética pixel-art / 8-bit, metáfora de prédio onde cada andar = área da vida.

![LOKI Banner](assets/loki_icon_64.png)

---

## 📖 Sobre o Projeto

**LOKI** é uma aplicação de gestão pessoal/operacional com estética **pixel-art / 8-bit**. A metáfora central é um **prédio** onde cada andar representa uma área da vida ou projeto.

Atualmente, o projeto inclui:

- **Tela de Introdução** — cena de rua com prédio de 2 andares, NPCs estilo RPG medieval, ciclo dia/noite dinâmico
- **Mecânica de Andares** — adicionar andares aleatórios ao prédio (11 tipos disponíveis)
- **Navegação por Scroll** — subir e descer para ver todos os andares
- **Backend FastAPI** — API REST para gestão de andares, salas, chat e widgets
- **Frontend React** — protótipo web (em pausa, foco no desktop)

---

## 🎮 Como Rodar

### Pré-requisitos

- **Python 3.12** (o pygame está instalado nesta versão)
- **Pygame 2.6.1**

### Executar o Jogo

No **CMD do Windows**:

```cmd
cd C:\Users\Gabriel\Desktop\HOME\LOKI
"C:\Users\Gabriel\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe" intro.py
```

### Controles

| Ação | Controle |
|------|----------|
| Adicionar andar | Botão **ADICIONAR ANDAR** (lateral direita) |
| Navegar para cima | Rodinha do mouse **para baixo** |
| Navegar para baixo | Rodinha do mouse **para cima** |
| Entrar no prédio | Botão **ENTER** |

---

## 📁 Estrutura do Projeto

```
LOKI/
├── intro.py              # Tela de introdução (Pygame)
├── _game.py              # Loop principal do jogo
├── settings.py           # Configurações e paleta de cores
├── api_client.py         # Cliente HTTP para FastAPI
├── sprites.py            # Renderização de sprites pixel-art
├── assets/               # Imagens e sprites
│   ├── andar_1.png       # 11 tipos de andares
│   ├── andar_2.png
│   ├── ...
│   ├── andar_11.png
│   └── loki_icon_*.png   # Ícones do projeto
├── scenes/               # Cenas do jogo (menu, prédio, sala, chat)
│   ├── base_scene.py
│   ├── menu_scene.py
│   ├── building_scene.py
│   ├── room_scene.py
│   └── chat_scene.py
├── backend/              # API FastAPI + SQLite
│   └── app/
│       ├── main.py
│       ├── db.py
│       ├── models.py
│       ├── schemas.py
│       └── crud.py
├── frontend/             # Protótipo React+Vite (pausado)
├── IDEA.md               # Ideia original
├── PLAN.md               # Planeamento
└── README.md             # Este ficheiro
```

---

## 🎨 Estilo Visual

- **Pixel art** estilo RPG medieval (tavernas, enxaimel, bandeiras, vitrais)
- **Ciclo dia/noite** dinâmico baseado no horário real
- **NPCs** com animação de passada
- **11 tipos de andares** com sprites únicos

---

## 🔧 Tecnologias

| Camada | Tecnologia |
|--------|------------|
| **Desktop** | Python 3.12 + Pygame 2.6.1 |
| **Backend** | FastAPI + SQLite |
| **Frontend** | React + Vite + Tailwind CSS (pausado) |
| **Imagens** | PIL/Pillow para processamento de sprites |

---

## 📝 Licença

Projeto pessoal de gestão e planeamento.

---

## 👤 Autor

**Gabriel** ([@COSMOS2505](https://github.com/COSMOS2505))
