"""Модуль для работы с SQLite."""

import sqlite3
from typing import Optional, Tuple


class DatabaseManager:
    """Менеджер подключения к SQLite."""

    def __init__(self, db_path: str = "nutrition_diary.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"OK: подключение к {self.db_path}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def execute(self, query: str, params: Optional[Tuple] = None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            self.connection.commit()
            return None
        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка запроса: {e}")
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()