import sqlite3, json
from typing import List, Dict, Any, Optional


class DB:
    def __init__(self, path: str):
        self.path = path
        self._init()

    def _init(self):
        with sqlite3.connect(self.path) as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  kind TEXT NOT NULL,       -- 'PHRASE' | 'ALLWORDS'
                  payload TEXT NOT NULL     -- JSON: {"text": "..."} або {"words": ["...","..."]}
                );
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                  key TEXT PRIMARY KEY,
                  value TEXT
                );
            """)

    # ===== rules =====
    def add_phrase(self, text: str) -> int:
        data = {"text": text}
        with sqlite3.connect(self.path) as c:
            cur = c.execute(
                "INSERT INTO rules(kind, payload) VALUES(?,?)",
                ("PHRASE", json.dumps(data, ensure_ascii=False))
            )
            return cur.lastrowid

    def add_allwords(self, words: List[str]) -> int:
        data = {"words": words}
        with sqlite3.connect(self.path) as c:
            cur = c.execute(
                "INSERT INTO rules(kind, payload) VALUES(?,?)",
                ("ALLWORDS", json.dumps(data, ensure_ascii=False))
            )
            return cur.lastrowid

    def del_rule(self, rule_id: int) -> bool:
        with sqlite3.connect(self.path) as c:
            cur = c.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            return cur.rowcount > 0

    def list_rules(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.path) as c:
            rows = c.execute("SELECT id, kind, payload FROM rules ORDER BY id ASC").fetchall()
        out: List[Dict[str, Any]] = []
        for rid, kind, payload in rows:
            data = json.loads(payload)
            data["id"] = rid
            data["kind"] = kind
            out.append(data)
        return out

    # ===== settings (на майбутнє) =====
    def get(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.path) as c:
            row = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        with sqlite3.connect(self.path) as c:
            c.execute("REPLACE INTO settings(key, value) VALUES(?,?)", (key, value))
