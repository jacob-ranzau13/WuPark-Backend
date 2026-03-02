
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_PATH = "ParkingLots.db"


def _get_conn():
    return sqlite3.connect(DB_PATH)

def table_setup() -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS ParkingLots (
        LotID INTEGER PRIMARY KEY,
        Timestamp TEXT NOT NULL,
        Status TEXT,
        Payload TEXT
    );
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    finally:
        conn.close()

def add_parking_lot(lot_id: int, status: Any, payload: Any) -> None:
    timestamp = datetime.utcnow().isoformat()
    status_json = json.dumps(status)
    payload_json = json.dumps(payload)

    sql = "INSERT INTO ParkingLots (LotID, Timestamp, Status, Payload) VALUES (?, ?, ?, ?);"
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, (lot_id, timestamp, status_json, payload_json))
        conn.commit()
    finally:
        conn.close()


def update_parking_lot(lot_id: int, status: Optional[Any] = None, payload: Optional[Any] = None) -> bool:
    if status is None and payload is None:
        return False

    timestamp = datetime.utcnow().isoformat()
    set_clauses = []
    params = []

    if status is not None:
        set_clauses.append("Status = ?")
        params.append(json.dumps(status))
    if payload is not None:
        set_clauses.append("Payload = ?")
        params.append(json.dumps(payload))

    set_clauses.append("Timestamp = ?")
    params.append(timestamp)

    params.append(lot_id)

    sql = f"UPDATE ParkingLots SET {', '.join(set_clauses)} WHERE LotID = ?;"

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_parking_lot(lot_id: int) -> Optional[Dict[str, Any]]:
    sql = "SELECT LotID, Timestamp, Status, Payload FROM ParkingLots WHERE LotID = ? LIMIT 1;"
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, (lot_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "LotID": row[0],
            "Timestamp": row[1],  # ISO string
            "Status": json.loads(row[2]),
            "Payload": json.loads(row[3])
        }
    finally:
        conn.close()


def get_all_parking_lots() -> List[Dict[str, Any]]:
    sql = "SELECT LotID, Timestamp, Status, Payload FROM ParkingLots;"
    conn = _get_conn()
    rows_out = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        for row in cur.fetchall():
            rows_out.append({
                "LotID": row[0],
                "Timestamp": row[1],
                "Status": json.loads(row[2]),
                "Payload": json.loads(row[3])
            })
        return rows_out
    finally:
        conn.close()


def delete_lot(lot_id: int) -> bool:
    sql = "DELETE FROM ParkingLots WHERE LotID = ?;"
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, (lot_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()



