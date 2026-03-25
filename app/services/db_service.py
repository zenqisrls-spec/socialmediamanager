from __future__ import annotations

import sqlite3
from pathlib import Path


class DBService:
    def __init__(self) -> None:
        self.db_path = Path(__file__).resolve().parents[2] / "data" / "app.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    openai_api_key TEXT DEFAULT '',
                    model_name TEXT DEFAULT 'gpt-4.1-mini',
                    require_human_approval INTEGER DEFAULT 1,
                    autopublish_enabled INTEGER DEFAULT 0,
                    whatsapp_enabled INTEGER DEFAULT 0,
                    meta_access_token TEXT DEFAULT '',
                    meta_page_id TEXT DEFAULT '',
                    whatsapp_token TEXT DEFAULT '',
                    whatsapp_phone_number_id TEXT DEFAULT '',
                    whatsapp_to TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS drafts (
                    id TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,
                    content TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS published (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    published_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO app_config(id) VALUES (1)
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO users(username, password, role) VALUES ('admin', 'admin123', 'admin')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO users(username, password, role) VALUES ('approver', 'approver123', 'approver')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO users(username, password, role) VALUES ('editor', 'editor123', 'editor')"
            )
            conn.commit()

