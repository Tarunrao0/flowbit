import sqlite3
from datetime import datetime

class SharedMemory:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self._init_db()
        
    def _init_db(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    def store(self, conversation_id: str, data: dict):
        self.conn.execute(
            "INSERT INTO conversations (conversation_id, data) VALUES (?, ?)",
            (conversation_id, str(data))
        )
        self.conn.commit()
    
    def append_to_conversation(self, conversation_id: str, data: dict):
        existing = self.retrieve_conversation(conversation_id)
        if existing:
            updated = {**existing, **data}
            self.conn.execute(
                "UPDATE conversations SET data = ? WHERE conversation_id = ?",
                (str(updated), conversation_id)
            )
        else:
            self.store(conversation_id, data)
        self.conn.commit()
    
    def retrieve_conversation(self, conversation_id: str) -> dict:
        cursor = self.conn.execute(
            "SELECT data FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        result = cursor.fetchone()
        return eval(result[0]) if result else None