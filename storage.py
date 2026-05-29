"""
EGX Pro Terminal v27 - Local Storage Engine
SQLite-based persistence with backup and optimization
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import shutil
import logging
from contextlib import contextmanager

from config.settings import db_config, app_config

logger = logging.getLogger(__name__)

class LocalStorage:
    def __init__(self):
        self.db_path = db_config.DB_PATH
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    target_price REAL,
                    stop_loss REAL,
                    notes TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    price REAL,
                    message TEXT,
                    severity TEXT DEFAULT 'info',
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtest_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    total_return REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    win_rate REAL,
                    total_trades INTEGER,
                    params TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    period TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    data_json TEXT,
                    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, period, interval)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    shares INTEGER NOT NULL,
                    avg_cost REAL NOT NULL,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    predicted_direction TEXT,
                    confidence REAL,
                    target_price REAL,
                    stop_loss REAL,
                    horizon_days INTEGER,
                    features_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully")

    def add_to_watchlist(self, symbol, target_price=None, stop_loss=None, notes=""):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO watchlist (symbol, target_price, stop_loss, notes, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (symbol.upper(), target_price, stop_loss, notes, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False

    def get_watchlist(self):
        try:
            with self._get_connection() as conn:
                df = pd.read_sql_query("SELECT * FROM watchlist ORDER BY added_at DESC", conn)
                return df
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return pd.DataFrame()

    def remove_from_watchlist(self, symbol):
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False

    def add_alert(self, symbol, alert_type, condition, price, message, severity="info"):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO alerts (symbol, alert_type, condition, price, message, severity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (symbol.upper(), alert_type, condition, price, message, severity))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            return False

    def get_alerts(self, symbol=None, limit=50, acknowledged=None):
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM alerts WHERE 1=1"
                params = []
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol.upper())
                if acknowledged is not None:
                    query += " AND acknowledged = ?"
                    params.append(int(acknowledged))
                query += " ORDER BY triggered_at DESC LIMIT ?"
                params.append(limit)
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return pd.DataFrame()

    def acknowledge_alert(self, alert_id):
        try:
            with self._get_connection() as conn:
                conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False

    def save_backtest(self, strategy_name, symbol, result):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO backtest_results 
                    (strategy_name, symbol, total_return, sharpe_ratio, max_drawdown, win_rate, total_trades, params)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    strategy_name, symbol.upper(),
                    result.get("total_return", 0),
                    result.get("sharpe_ratio", 0),
                    result.get("max_drawdown", 0),
                    result.get("win_rate", 0),
                    result.get("total_trades", 0),
                    json.dumps(result.get("params", {}))
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving backtest: {e}")
            return False

    def get_backtests(self, symbol=None, limit=20):
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM backtest_results WHERE 1=1"
                params = []
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol.upper())
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            logger.error(f"Error getting backtests: {e}")
            return pd.DataFrame()

    def save_analysis_cache(self, symbol, period, interval, data):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO analysis_cache (symbol, period, interval, data_json, computed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (symbol.upper(), period, interval, json.dumps(data), datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving analysis cache: {e}")
            return False

    def get_analysis_cache(self, symbol, period, interval):
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT data_json, computed_at FROM analysis_cache
                    WHERE symbol = ? AND period = ? AND interval = ?
                """, (symbol.upper(), period, interval))
                row = cursor.fetchone()
                if row:
                    computed_at = datetime.fromisoformat(row["computed_at"])
                    if (datetime.now() - computed_at).seconds < app_config.CACHE_TTL_ANALYSIS:
                        return json.loads(row["data_json"])
                return None
        except Exception as e:
            logger.error(f"Error getting analysis cache: {e}")
            return None

    def save_prediction(self, symbol, prediction):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO predictions (symbol, predicted_direction, confidence, target_price, stop_loss, horizon_days, features_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol.upper(), prediction.get("direction"),
                    prediction.get("confidence"), prediction.get("target_price"),
                    prediction.get("stop_loss"), prediction.get("horizon_days"),
                    json.dumps(prediction.get("features", {}))
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return False

    def get_predictions(self, symbol=None, limit=50):
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM predictions WHERE 1=1"
                params = []
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol.upper())
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            logger.error(f"Error getting predictions: {e}")
            return pd.DataFrame()

    def get_stats(self):
        try:
            with self._get_connection() as conn:
                stats = {}
                for table in ["watchlist", "alerts", "backtest_results", "analysis_cache", "predictions"]:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]

                db_size = os.path.getsize(self.db_path)
                stats["size_bytes"] = db_size
                stats["size_mb"] = round(db_size / (1024 * 1024), 2)
                return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(db_config.BACKUP_DIR, f"egx_db_backup_{timestamp}.db")
            shutil.copy2(self.db_path, backup_path)

            backups = sorted([
                f for f in os.listdir(db_config.BACKUP_DIR)
                if f.startswith("egx_db_backup_")
            ])
            while len(backups) > db_config.MAX_BACKUPS:
                os.remove(os.path.join(db_config.BACKUP_DIR, backups.pop(0)))

            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def vacuum(self):
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                conn.commit()
                logger.info("Database vacuumed successfully")
                return True
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            return False

    def clear_old_data(self, days=90):
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            with self._get_connection() as conn:
                conn.execute("DELETE FROM alerts WHERE triggered_at < ?", (cutoff,))
                conn.execute("DELETE FROM predictions WHERE created_at < ?", (cutoff,))
                conn.commit()
                logger.info(f"Cleared data older than {days} days")
                return True
        except Exception as e:
            logger.error(f"Error clearing old data: {e}")
            return False

local_storage = LocalStorage()
