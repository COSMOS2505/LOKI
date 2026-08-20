from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.db import get_db, init_db
from app import crud
from app.schemas import (
    FloorCreate, FloorUpdate, FloorOut,
    WidgetCreate, WidgetOut,
    WidgetDataOut, ChatMessageOut,
    ChatRequest,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Loki API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _floor_to_dict(f: FloorOut):
    return {
        "id": f.id,
        "name": f.name,
        "purpose": f.purpose,
        "color": f.color,
        "order_index": f.order_index,
        "status_summary": f.status_summary,
        "agent_system_prompt": f.agent_system_prompt,
        "agent_memory": f.agent_memory,
        "created_at": f.created_at,
        "is_archived": f.is_archived,
    }

@app.get("/api/floors")
def get_floors(db: Session = Depends(get_db)):
    floors = crud.list_floors(db)
    return [_floor_to_dict(FloorOut.model_validate(f)) for f in floors]

@app.post("/api/floors", response_model=FloorOut)
def create_floor(data: FloorCreate, db: Session = Depends(get_db)):
    floor = crud.create_floor(db, data.model_dump())
    return FloorOut.model_validate(floor)

@app.put("/api/floors/{floor_id}", response_model=FloorOut)
def update_floor(floor_id: int, data: FloorUpdate, db: Session = Depends(get_db)):
    floor = crud.update_floor(db, floor_id, data.model_dump(exclude_unset=True))
    if not floor:
        return {"error": "Floor not found"}
    return FloorOut.model_validate(floor)

@app.delete("/api/floors/{floor_id}")
def delete_floor(floor_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_floor(db, floor_id)
    if not ok:
        return {"error": "Floor not found"}
    return {"ok": True}

@app.get("/api/floors/{floor_id}/widgets")
def get_widgets(floor_id: int, db: Session = Depends(get_db)):
    widgets = crud.list_widgets(db, floor_id)
    return [WidgetOut.model_validate(w) for w in widgets]

@app.post("/api/floors/{floor_id}/widgets", response_model=WidgetOut)
def create_widget(floor_id: int, data: WidgetCreate, db: Session = Depends(get_db)):
    widget = crud.create_widget(db, floor_id, data.widget_type, data.config)
    return WidgetOut.model_validate(widget)

@app.get("/api/floors/{floor_id}/chat")
def get_chat(floor_id: int, db: Session = Depends(get_db)):
    messages = crud.list_chat_messages(db, floor_id)
    return [ChatMessageOut.model_validate(m) for m in messages]

from app.models import Floor, ChatMessage, Widget
from app.schemas import ChatMessageOut

@app.post("/api/floors/{floor_id}/widgets", response_model=WidgetOut)
def create_widget(floor_id: int, data: WidgetCreate, db: Session = Depends(get_db)):
    widget = crud.create_widget(db, floor_id, data.widget_type, data.config)
    return WidgetOut.model_validate(widget)

@app.get("/api/widgets/{widget_id}/data")
def chat(data: ChatRequest, db: Session = Depends(get_db)):
    msg = crud.add_chat_message(db, data.floor_id, "user", data.message)
    # Placeholder para resposta do agente
    agent_reply = f"[Agente da sala '{data.floor_id}'] Recebido: {data.message}"
    crud.add_chat_message(db, data.floor_id, "agent", agent_reply)
    return {
        "user_message": ChatMessageOut.model_validate(msg),
        "agent_reply": agent_reply,
    }

@app.get("/api/widgets/{widget_id}/data")
def get_widget_data(widget_id: int, db: Session = Depends(get_db)):
    wd = crud.get_widget_data(db, widget_id)
    if not wd:
        return {"payload": {}}
    return {"id": wd.id, "widget_id": wd.widget_id, "payload": json.loads(wd.payload), "updated_at": wd.updated_at}

@app.put("/api/widgets/{widget_id}/data")
def set_widget_data(widget_id: int, payload: dict, db: Session = Depends(get_db)):
    wd = crud.set_widget_data(db, widget_id, payload)
    return WidgetDataOut.model_validate(wd)
