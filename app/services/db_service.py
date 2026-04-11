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
                    client_id TEXT NOT NULL DEFAULT '',
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

                CREATE TABLE IF NOT EXISTS campaign_batches (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL DEFAULT '',
                    name TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL DEFAULT '',
                    batch_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    campaign_name TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    target_audience TEXT NOT NULL,
                    daily_budget_eur REAL NOT NULL,
                    ad_copy TEXT NOT NULL,
                    creative_direction TEXT NOT NULL,
                    kpi_target TEXT NOT NULL,
                    creative_brief_image TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(batch_id) REFERENCES campaign_batches(id)
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    website TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    city TEXT NOT NULL,
                    unique_value TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    openai_api_key TEXT NOT NULL DEFAULT '',
                    model_name TEXT NOT NULL DEFAULT 'gpt-4.1-mini',
                    require_human_approval INTEGER NOT NULL DEFAULT 1,
                    autopublish_enabled INTEGER NOT NULL DEFAULT 0,
                    whatsapp_enabled INTEGER NOT NULL DEFAULT 0,
                    meta_access_token TEXT NOT NULL DEFAULT '',
                    meta_page_id TEXT NOT NULL DEFAULT '',
                    meta_ad_account_id TEXT NOT NULL DEFAULT '',
                    whatsapp_token TEXT NOT NULL DEFAULT '',
                    whatsapp_phone_number_id TEXT NOT NULL DEFAULT '',
                    whatsapp_to TEXT NOT NULL DEFAULT '',
                    google_ads_customer_id TEXT NOT NULL DEFAULT '',
                    google_ads_developer_token TEXT NOT NULL DEFAULT '',
                    google_ads_refresh_token TEXT NOT NULL DEFAULT '',
                    google_ads_client_id TEXT NOT NULL DEFAULT '',
                    google_ads_client_secret TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    role TEXT NOT NULL,
                    expires_at TEXT NOT NULL
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
            columns = [r[1] for r in conn.execute("PRAGMA table_info(campaigns)").fetchall()]
            if "creative_brief_image" not in columns:
                conn.execute("ALTER TABLE campaigns ADD COLUMN creative_brief_image TEXT NOT NULL DEFAULT ''")
            client_columns = [r[1] for r in conn.execute("PRAGMA table_info(clients)").fetchall()]
            needed_client_columns = {
                "openai_api_key": "ALTER TABLE clients ADD COLUMN openai_api_key TEXT NOT NULL DEFAULT ''",
                "model_name": "ALTER TABLE clients ADD COLUMN model_name TEXT NOT NULL DEFAULT 'gpt-4.1-mini'",
                "require_human_approval": "ALTER TABLE clients ADD COLUMN require_human_approval INTEGER NOT NULL DEFAULT 1",
                "autopublish_enabled": "ALTER TABLE clients ADD COLUMN autopublish_enabled INTEGER NOT NULL DEFAULT 0",
                "whatsapp_enabled": "ALTER TABLE clients ADD COLUMN whatsapp_enabled INTEGER NOT NULL DEFAULT 0",
                "meta_access_token": "ALTER TABLE clients ADD COLUMN meta_access_token TEXT NOT NULL DEFAULT ''",
                "meta_page_id": "ALTER TABLE clients ADD COLUMN meta_page_id TEXT NOT NULL DEFAULT ''",
                "meta_ad_account_id": "ALTER TABLE clients ADD COLUMN meta_ad_account_id TEXT NOT NULL DEFAULT ''",
                "whatsapp_token": "ALTER TABLE clients ADD COLUMN whatsapp_token TEXT NOT NULL DEFAULT ''",
                "whatsapp_phone_number_id": "ALTER TABLE clients ADD COLUMN whatsapp_phone_number_id TEXT NOT NULL DEFAULT ''",
                "whatsapp_to": "ALTER TABLE clients ADD COLUMN whatsapp_to TEXT NOT NULL DEFAULT ''",
                "google_ads_customer_id": "ALTER TABLE clients ADD COLUMN google_ads_customer_id TEXT NOT NULL DEFAULT ''",
                "google_ads_developer_token": "ALTER TABLE clients ADD COLUMN google_ads_developer_token TEXT NOT NULL DEFAULT ''",
                "google_ads_refresh_token": "ALTER TABLE clients ADD COLUMN google_ads_refresh_token TEXT NOT NULL DEFAULT ''",
                "google_ads_client_id": "ALTER TABLE clients ADD COLUMN google_ads_client_id TEXT NOT NULL DEFAULT ''",
                "google_ads_client_secret": "ALTER TABLE clients ADD COLUMN google_ads_client_secret TEXT NOT NULL DEFAULT ''",
            }
            for col, ddl in needed_client_columns.items():
                if col not in client_columns:
                    conn.execute(ddl)
            draft_columns = [r[1] for r in conn.execute("PRAGMA table_info(drafts)").fetchall()]
            if "client_id" not in draft_columns:
                conn.execute("ALTER TABLE drafts ADD COLUMN client_id TEXT NOT NULL DEFAULT ''")
            campaign_batch_columns = [r[1] for r in conn.execute("PRAGMA table_info(campaign_batches)").fetchall()]
            if "client_id" not in campaign_batch_columns:
                conn.execute("ALTER TABLE campaign_batches ADD COLUMN client_id TEXT NOT NULL DEFAULT ''")
            campaign_columns = [r[1] for r in conn.execute("PRAGMA table_info(campaigns)").fetchall()]
            if "client_id" not in campaign_columns:
                conn.execute("ALTER TABLE campaigns ADD COLUMN client_id TEXT NOT NULL DEFAULT ''")
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
