# Loki — Planeamento

## Visão Geral
Aplicação modular (web local / desktop) de gerenciamento pessoal e operacional com interface pixel art / estética de hotel retrô. Metáfora: **prédio de andares**, onde cada andar = área de vida/negócio.

## Stack

- **Frontend:** React + Vite + Tailwind CSS (estático, roda no navegador)
- **Backend:** Python FastAPI + SQLite (servidor local, porta 8421)
- **IA:** Cliente HTTP para `inference-api.nousresearch.com/v1` (Hermes/Nous)
- **Visual:** Pixel-art via CSS + SVG inline (sem sprites externos na fase 1)
- **Empacotamento final:** Tauri — frontend + backend embedados → `.exe` standalone (Fase 2)

## Por que essa stack?
- React: UI complexa (chat, CRUD, formulários, animações) é rápido.
- FastAPI + SQLite: backend leve, persistência local, zero servidor externo.
- Vite: dev server instantâneo, build estático simples.
- Tauri (fase 2): empacota tudo num `.exe` único com backend Rust.

## Estrutura de Pastas

```
Loki/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── db.py
│   │   └── agents.py
│   ├── data/
│   │   └── loki.db
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── building/
│   │   │   ├── Building.jsx
│   │   │   ├── FloorCard.jsx
│   │   │   └── FloorModal.jsx
│   │   ├── room/
│   │   │   ├── Room.jsx
│   │   │   ├── Agent.jsx
│   │   │   ├── ChatPanel.jsx
│   │   │   └── widgets/
│   │   └── api.js
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── PLAN.md
└── README.md
```

## Banco de Dados (SQLite)

### Tabela `floors` — Andares / Salas
| coluna             | tipo    | descrição                          |
|--------------------|---------|------------------------------------|
| id                 | INTEGER | PK autoincrement                   |
| name               | TEXT    | nome do andar                      |
| purpose            | TEXT    | propósito da sala                  |
| color              | TEXT    | cor temática hex                   |
| order_index        | INTEGER | posição no prédio                 |
| status_summary     | TEXT    | resumo de status                  |
| agent_system_prompt| TEXT    | system prompt do agente da sala   |
| agent_memory       | TEXT    | JSON texto, memória persistente   |
| created_at         | TIMESTAMP | data de criação                 |
| is_archived        | INTEGER | 0=ativo, 1=arquivado              |

### Tabela `widgets` — Ferramentas da sala
| coluna       | tipo     | descrição                     |
|-------------|----------|-------------------------------|
| id          | INTEGER  | PK                            |
| floor_id    | INTEGER  | FK → floors(id)               |
| widget_type | TEXT     | 'financeiro', 'ordens', etc. |
| config      | TEXT     | JSON config do widget         |
| created_at  | TIMESTAMP|                               |

### Tabela `widget_data` — Dados dos widgets
| coluna    | tipo     | descrição                 |
|----------|----------|---------------------------|
| id       | INTEGER  | PK                        |
| widget_id| INTEGER  | FK → widgets(id)          |
| payload  | TEXT     | JSON dos dados            |
| updated_at| TIMESTAMP|                          |

### Tabela `chat_messages` — Histórico do agente
| coluna    | tipo     | descrição                |
|----------|----------|--------------------------|
| id       | INTEGER  | PK                       |
| floor_id | INTEGER  | FK → floors(id)          |
| role     | TEXT     | 'user' ou 'agent'        |
| content  | TEXT     | conteúdo da mensagem     |
| created_at| TIMESTAMP|                         |

## Fluxo de Dados

```
[Lobby] → lista andares do DB → FloorCard → onClick → [Room]
[Room] → carrega widgets da sala + histórico de chat
[Agente NPC] → clique abre ChatPanel
[ChatPanel] → envia prompt + contexto da sala para inference API → resposta → salva no DB
[Widget] → agente pode ler/modificar widget_data via API
```

## Roadmap

### Fase 0 — Foundation (agora)
- Backend FastAPI minimalista com SQLite (CRUD de andares)
- Frontend React: Lobby (prédio) + transição para sala vazia + modal de CRUD de andar
- Visual: prédio pixel art + cards de andar

### Fase 1 — Sala + Agente
- Sala interior com layout 2D (mesa, agente NPC clicável, widgets)
- ChatPanel integrado ao agente da sala
- Persistência de histórico de chat

### Fase 2 — Widgets
- Widget factory: financeiro (tabela de despesas), ordens (fila de pedidos), posts (planejador Instagram)
- Agente com function calling para ler/modificar widget_data

### Fase 3 — Estética aprofundada
- Animações de transição entre andares
- Sprites de agente animados (se necessário)
- Detalhes pixel art avançados

### Fase 4 — Empacotamento
- Tauri: frontend + backend → `.exe` standalone
- Ou PyInstaller se ficar tudo em Python
