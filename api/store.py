"""SQLite storage for the demo (stdlib sqlite3 only).

Readings are simulated on demand and cached here so the dashboard, reports
and exports read the same data. Support tickets and settings live here too.
The database file is local only and is gitignored.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.environ.get("TRAFFIC_DB", os.path.join(os.path.dirname(__file__), "..", "data", "traffic.sqlite"))


def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id TEXT NOT NULL,
                sensor_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                vehicle_count INTEGER NOT NULL,
                avg_speed_kmh REAL NOT NULL,
                occupancy_percent REAL NOT NULL,
                queue_length INTEGER NOT NULL,
                weather TEXT NOT NULL,
                event INTEGER NOT NULL,
                congestion TEXT NOT NULL,
                UNIQUE(intersection_id, timestamp)
            );
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id TEXT,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL,
                acknowledged INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL DEFAULT 'Open',
                reply TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        defaults = {
            "city_name": "Demo City (fictional)",
            "contact_email": "",
            "contact_phone": "",
            "congestion_alert_threshold": "High",
            "green_time_base_seconds": "30",
        }
        for k, v in defaults.items():
            conn.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (k, v))
        conn.commit()


def save_readings(readings: list[dict]) -> None:
    with connect() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO readings
               (intersection_id, sensor_id, timestamp, vehicle_count, avg_speed_kmh,
                occupancy_percent, queue_length, weather, event, congestion)
               VALUES (:intersection_id, :sensor_id, :timestamp, :vehicle_count,
                       :avg_speed_kmh, :occupancy_percent, :queue_length, :weather,
                       :event, :congestion)""",
            [{**r, "event": 1 if r["event"] else 0} for r in readings],
        )
        conn.commit()


def recent_readings(intersection_id: str | None = None, limit: int = 50) -> list[dict]:
    with connect() as conn:
        if intersection_id:
            rows = conn.execute(
                "SELECT * FROM readings WHERE intersection_id=? ORDER BY timestamp DESC LIMIT ?",
                (intersection_id, limit)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM readings ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["event"] = bool(d["event"])
        out.append(d)
    return out


def get_settings() -> dict:
    with connect() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}


def set_settings(values: dict) -> dict:
    with connect() as conn:
        for k, v in values.items():
            conn.execute("INSERT INTO settings(key, value) VALUES (?, ?) "
                         "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, str(v)))
        conn.commit()
    return get_settings()


def list_alerts() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 100").fetchall()
    return [dict(r) for r in rows]


def add_alert(intersection_id, type_, message, severity) -> dict:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO alerts(intersection_id, type, message, severity, created_at) VALUES (?,?,?,?,?)",
            (intersection_id, type_, message, severity, now))
        conn.commit()
        row = conn.execute("SELECT * FROM alerts WHERE id=?", (cur.lastrowid,)).fetchone()
    return dict(row)


def acknowledge_alert(alert_id: int) -> dict | None:
    with connect() as conn:
        conn.execute("UPDATE alerts SET acknowledged=1 WHERE id=?", (alert_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
    return dict(row) if row else None


def list_tickets() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM support_tickets ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def create_ticket(name, subject, message, priority) -> dict:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO support_tickets(name, subject, message, priority, created_at) VALUES (?,?,?,?,?)",
            (name, subject, message, priority, now))
        conn.commit()
        row = conn.execute("SELECT * FROM support_tickets WHERE id=?", (cur.lastrowid,)).fetchone()
    return dict(row)


def update_ticket(ticket_id: int, status: str | None, reply: str | None) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM support_tickets WHERE id=?", (ticket_id,)).fetchone()
        if not row:
            return None
        if status:
            conn.execute("UPDATE support_tickets SET status=? WHERE id=?", (status, ticket_id))
        if reply is not None:
            conn.execute("UPDATE support_tickets SET reply=? WHERE id=?", (reply, ticket_id))
        conn.commit()
        row = conn.execute("SELECT * FROM support_tickets WHERE id=?", (ticket_id,)).fetchone()
    return dict(row)


def report_summary() -> dict:
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM readings").fetchone()["c"]
        by_level = conn.execute(
            "SELECT congestion, COUNT(*) c FROM readings GROUP BY congestion").fetchall()
        by_inter = conn.execute(
            "SELECT intersection_id, AVG(vehicle_count) avg_count, MAX(occupancy_percent) max_occ, COUNT(*) n "
            "FROM readings GROUP BY intersection_id ORDER BY avg_count DESC").fetchall()
    return {
        "total_readings": total,
        "by_congestion": {r["congestion"]: r["c"] for r in by_level},
        "by_intersection": [dict(r) for r in by_inter],
    }
