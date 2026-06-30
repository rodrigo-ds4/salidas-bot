"""Memory manager para Salidas Bot - Corto y largo plazo"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, List

# ===================== SHORT-TERM MEMORY (Sesión) =====================

class ShortTermMemory:
    """Memoria de corto plazo en memoria (se pierde al reiniciar)"""
    
    def __init__(self):
        self.data = {
            "conversation_history": [],
            "user_context": {},
            "current_session": datetime.now().isoformat(),
            "session_metadata": {}
        }
    
    def add_message(self, role: str, content: str):
        """Añade un mensaje a la conversación"""
        self.data["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_recent_context(self, limit: int = 5) -> List[dict]:
        """Retorna los últimos N mensajes"""
        return self.data["conversation_history"][-limit:]
    
    def set_user_context(self, key: str, value: Any):
        """Almacena contexto del usuario actual"""
        self.data["user_context"][key] = value
    
    def get_user_context(self, key: str) -> Optional[Any]:
        """Obtiene contexto del usuario"""
        return self.data["user_context"].get(key)
    
    def clear(self):
        """Limpia la memoria de sesión"""
        self.data = {
            "conversation_history": [],
            "user_context": {},
            "current_session": datetime.now().isoformat(),
            "session_metadata": {}
        }


# ===================== LONG-TERM MEMORY (Persistente) =====================

class LongTermMemory:
    """Memoria de largo plazo usando SQLite"""
    
    def __init__(self, db_path: str = "memory/salidas_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de conversaciones históricas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    user_id TEXT,
                    messages TEXT NOT NULL,
                    summary TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de preferencias de usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL UNIQUE,
                    preferences TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de lugares favoritos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorite_places (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    place_name TEXT NOT NULL,
                    category TEXT,
                    rating REAL,
                    notes TEXT,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_conversation(self, messages: List[dict], user_id: str = "default", summary: str = ""):
        """Guarda una conversación completa"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (date, user_id, messages, summary)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                user_id,
                json.dumps(messages, ensure_ascii=False),
                summary
            ))
            conn.commit()
    
    def get_user_history(self, user_id: str = "default", days: int = 7) -> List[dict]:
        """Obtiene el historial de un usuario de los últimos N días"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE user_id = ? AND date >= ?
                ORDER BY created_at DESC
            """, (user_id, cutoff_date))
            
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "date": row[1],
                    "user_id": row[2],
                    "messages": json.loads(row[3]),
                    "summary": row[4],
                    "created_at": row[5]
                }
                for row in rows
            ]
    
    def save_user_preference(self, user_id: str, preferences: dict):
        """Guarda preferencias del usuario"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (user_id, preferences)
                VALUES (?, ?)
            """, (user_id, json.dumps(preferences, ensure_ascii=False)))
            conn.commit()
    
    def get_user_preferences(self, user_id: str = "default") -> dict:
        """Obtiene preferencias del usuario"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preferences FROM user_preferences WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return {}
    
    def add_favorite_place(self, user_id: str, place_name: str, category: str, rating: float, notes: str = ""):
        """Añade un lugar a favoritos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO favorite_places (user_id, place_name, category, rating, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, place_name, category, rating, notes))
            conn.commit()
    
    def get_favorite_places(self, user_id: str = "default") -> List[dict]:
        """Obtiene los lugares favoritos de un usuario"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM favorite_places 
                WHERE user_id = ?
                ORDER BY added_at DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "place_name": row[2],
                    "category": row[3],
                    "rating": row[4],
                    "notes": row[5],
                    "added_at": row[6]
                }
                for row in rows
            ]


# ===================== MEMORY MANAGER =====================

class MemoryManager:
    """Gestor unificado de memoria (corto + largo plazo)"""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.current_user = "default"
    
    def set_user(self, user_id: str):
        """Cambia el usuario actual"""
        self.current_user = user_id
    
    def add_message(self, role: str, content: str):
        """Añade mensaje a memoria corta"""
        self.short_term.add_message(role, content)
    
    def get_context(self) -> dict:
        """Retorna contexto completo para el agent"""
        return {
            "recent_messages": self.short_term.get_recent_context(5),
            "user_preferences": self.long_term.get_user_preferences(self.current_user),
            "favorite_places": self.long_term.get_favorite_places(self.current_user),
            "user_context": self.short_term.data["user_context"]
        }
    
    def save_session(self, summary: str = ""):
        """Guarda la sesión actual en memoria larga"""
        self.long_term.save_conversation(
            self.short_term.data["conversation_history"],
            self.current_user,
            summary
        )
