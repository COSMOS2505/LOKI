import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Floor, Widget, WidgetData, ChatMessage

def _now():
    return datetime.now(timezone.utc).isoformat()

def list_floors(db: Session, archived: bool = False):
    query = db.query(Floor).order_by(Floor.order_index.asc(), Floor.created_at.asc())
    if not archived:
        query = query.filter(Floor.is_archived == False)
    return query.all()

def get_floor(db: Session, floor_id: int):
    return db.query(Floor).filter(Floor.id == floor_id).first()

def create_floor(db: Session, data: dict) -> Floor:
    last = db.query(Floor).order_by(Floor.order_index.desc()).first()
    order_index = (last.order_index + 1) if last else 1
    now = _now()
    floor = Floor(
        name=data["name"],
        purpose=data.get("purpose"),
        color=data.get("color", "#4ade80"),
        order_index=order_index,
        status_summary=data.get("status_summary"),
        agent_system_prompt=data.get("agent_system_prompt"),
        agent_memory=data.get("agent_memory"),
        created_at=now,
        is_archived=False,
    )
    db.add(floor)
    db.commit()
    db.refresh(floor)
    return floor

def update_floor(db: Session, floor_id: int, data: dict) -> Floor | None:
    floor = get_floor(db, floor_id)
    if not floor:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(floor, key, value)
    db.commit()
    db.refresh(floor)
    return floor

def delete_floor(db: Session, floor_id: int) -> bool:
    floor = get_floor(db, floor_id)
    if not floor:
        return False
    db.delete(floor)
    db.commit()
    return True

def list_widgets(db: Session, floor_id: int):
    return db.query(Widget).filter(Widget.floor_id == floor_id).all()

def create_widget(db: Session, floor_id: int, widget_type: str, config: dict | None = None) -> Widget:
    now = _now()
    widget = Widget(
        floor_id=floor_id,
        widget_type=widget_type,
        config=json.dumps(config or {}),
        created_at=now,
    )
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget

def get_widget_data(db: Session, widget_id: int) -> WidgetData | None:
    return db.query(WidgetData).filter(WidgetData.widget_id == widget_id).first()

def set_widget_data(db: Session, widget_id: int, payload: dict) -> WidgetData:
    now = _now()
    existing = db.query(WidgetData).filter(WidgetData.widget_id == widget_id).first()
    if existing:
        existing.payload = json.dumps(payload)
        existing.updated_at = now
    else:
        existing = WidgetData(
            widget_id=widget_id,
            payload=json.dumps(payload),
            updated_at=now,
        )
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing

def list_chat_messages(db: Session, floor_id: int):
    return db.query(ChatMessage).filter(ChatMessage.floor_id == floor_id).order_by(ChatMessage.created_at.asc()).all()

def add_chat_message(db: Session, floor_id: int, role: str, content: str) -> ChatMessage:
    now = _now()
    msg = ChatMessage(floor_id=floor_id, role=role, content=content, created_at=now)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
