from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=True, default="#4ade80")
    order_index: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    status_summary: Mapped[str] = mapped_column(Text, nullable=True)
    agent_system_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    agent_memory: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(30), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    floor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    widget_type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(30), nullable=True)

class WidgetData(Base):
    __tablename__ = "widget_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    widget_id: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[str] = mapped_column(String(30), nullable=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    floor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(30), nullable=True)
