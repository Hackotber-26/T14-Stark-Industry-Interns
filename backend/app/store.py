"""SQLite result ledger and evidence hashes."""
from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / 'data/fixcheck.db'


@contextmanager
def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute('CREATE TABLE IF NOT EXISTS results (id TEXT PRIMARY KEY, complaint_id TEXT, verdict TEXT, json TEXT, created_at TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS hashes (complaint_id TEXT, after_hash TEXT, UNIQUE(complaint_id, after_hash))')
    try:
        with db:
            yield db
    finally:
        db.close()


def save_result(result: dict) -> None:
    """Persist a complete verification result."""
    with _connect() as db:
        db.execute('INSERT OR REPLACE INTO results VALUES (?,?,?,?,?)', (result['id'], result['complaint_id'], result['verdict'], json.dumps(result), result['created_at']))


def list_results() -> list[dict]:
    """Return newest results first."""
    with _connect() as db:
        return [json.loads(row[0]) for row in db.execute('SELECT json FROM results ORDER BY created_at DESC, rowid DESC')]


def get_result(id: str) -> dict | None:
    """Find a result by its public id."""
    with _connect() as db:
        row = db.execute('SELECT json FROM results WHERE id=?', (id,)).fetchone()
    return json.loads(row[0]) if row else None


def add_hash(complaint_id: str, after_hash: str) -> None:
    """Register evidence without duplicating identical entries."""
    with _connect() as db:
        db.execute('INSERT OR IGNORE INTO hashes VALUES (?,?)', (complaint_id, after_hash))


def all_hashes() -> list[tuple[str, str]]:
    """Read the known evidence hashes."""
    with _connect() as db:
        return db.execute('SELECT complaint_id, after_hash FROM hashes ORDER BY rowid').fetchall()
