from pydantic import BaseModel

class FloorCreate(BaseModel):
    name: str
    purpose: str | None = None
    color: str | None = None
    status_summary: str | None = None
    agent_system_prompt: str | None = None
    agent_memory: str | None = None

class FloorUpdate(BaseModel):
    name: str | None = None
    purpose: str | None = None
    color: str | None = None
    status_summary: str | None = None
    agent_system_prompt: str | None = None
    agent_memory: str | None = None
    is_archived: bool | None = None

class FloorOut(BaseModel):
    id: int
    name: str
    purpose: str | None
    color: str
    order_index: int | None
    status_summary: str | None
    agent_system_prompt: str | None
    agent_memory: str | None
    created_at: str | None
    is_archived: bool
    class Config:
        from_attributes = True

class WidgetCreate(BaseModel):
    floor_id: int
    widget_type: str
    config: dict | None = None

class WidgetOut(BaseModel):
    id: int
    floor_id: int
    widget_type: str
    config: dict | None
    created_at: str | None
    class Config:
        from_attributes = True

class WidgetDataOut(BaseModel):
    id: int
    widget_id: int
    payload: dict
    updated_at: str | None
    class Config:
        from_attributes = True

class ChatMessageOut(BaseModel):
    id: int
    floor_id: int
    role: str
    content: str
    created_at: str | None
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    floor_id: int
    message: str
    system_prompt: str | None = None
    agent_memory: str | None = None
