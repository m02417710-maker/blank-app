"""
EGX Pro Terminal v34 - Data Storage Module
SQLite-based local storage for alerts, watchlists, and user preferences
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

class LocalStorage:
    def __init__(self, db_path: str = "data/egx_terminal.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    target_value REAL,
                    severity TEXT DEFAULT 'MEDIUM',
                    created_at TEXT,
                    triggered_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    metadata TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    symbols TEXT NOT NULL,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER,
                    price REAL,
                    total_value REAL,
                    strategy TEXT,
                    executed_at TEXT
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully")

    def save_alert(self, alert: Dict[str, Any]) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO alerts 
                    (id, symbol, alert_type, target_value, severity, created_at, triggered_at, is_active, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.get("id"),
                    alert.get("symbol"),
                    alert.get("type", alert.get("alert_type")),
                    alert.get("target", alert.get("target_value")),
                    alert.get("severity", "MEDIUM"),
                    alert.get("created", datetime.now().isoformat()),
                    alert.get("triggered_at"),
                    1 if alert.get("triggered", False) else 0,
                    json.dumps(alert.get("metadata", {}))
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
            return False

    def get_alerts(self, active_only: bool = True) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if active_only:
                    cursor.execute("SELECT * FROM alerts WHERE is_active = 1 ORDER BY created_at DESC")
                else:
                    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving alerts: {e}")
            return []

    def delete_alert(self, alert_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return False

    def save_watchlist(self, name: str, symbols: List[str]) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO watchlists (name, symbols, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (name, json.dumps(symbols), datetime.now().isoformat(), datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving watchlist: {e}")
            return False

    def get_watchlist(self, name: str = "default") -> List[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT symbols FROM watchlists WHERE name = ?", (name,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return []
        except Exception as e:
            logger.error(f"Error retrieving watchlist: {e}")
            return []

    def save_preference(self, key: str, value: Any) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO preferences (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, json.dumps(value), datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving preference: {e}")
            return False

    def get_preference(self, key: str, default: Any = None) -> Any:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return default
        except Exception as e:
            logger.error(f"Error retrieving preference: {e}")
            return default

    def save_trade(self, trade: Dict[str, Any]) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO trades (symbol, action, quantity, price, total_value, strategy, executed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade.get("symbol"),
                    trade.get("action"),
                    trade.get("quantity"),
                    trade.get("price"),
                    trade.get("total_value"),
                    trade.get("strategy"),
                    trade.get("executed_at", datetime.now().isoformat())
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return False

    def get_trade_history(self, symbol: Optional[str] = None) -> pd.DataFrame:
        try:
            with sqlite3.connect(self.db_path) as conn:
                if symbol:
                    query = "SELECT * FROM trades WHERE symbol = ? ORDER BY executed_at DESC"
                    df = pd.read_sql_query(query, conn, params=(symbol,))
                else:
                    query = "SELECT * FROM trades ORDER BY executed_at DESC"
                    df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            logger.error(f"Error retrieving trade history: {e}")
            return pd.DataFrame()

    def get_stats(self) -> Dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                stats = {}
                for table in ["alerts", "watchlists", "trades"]:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

local_storage = LocalStorage()
