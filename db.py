import sqlite3, json
def _init(self):
with sqlite3.connect(self.path) as c:
c.execute(
"""
CREATE TABLE IF NOT EXISTS rules (
id INTEGER PRIMARY KEY AUTOINCREMENT,
kind TEXT NOT NULL, -- 'PHRASE' | 'ALLWORDS'
payload TEXT NOT NULL -- JSON: {"text": "..."} або {"words": [..]}
);
"""
)
c.execute(
"""
CREATE TABLE IF NOT EXISTS settings (
key TEXT PRIMARY KEY,
value TEXT
);
"""
)


# ===== rules =====
def add_phrase(self, text: str) -> int:
data = {"text": text}
with sqlite3.connect(self.path) as c:
cur = c.execute("INSERT INTO rules(kind, payload) VALUES(?,?)", ("PHRASE", json.dumps(data)))
return cur.lastrowid


def add_allwords(self, words: List[str]) -> int:
data = {"words": words}
with sqlite3.connect(self.path) as c:
cur = c.execute("INSERT INTO rules(kind, payload) VALUES(?,?)", ("ALLWORDS", json.dumps(data)))
return cur.lastrowid


def del_rule(self, rule_id: int) -> bool:
with sqlite3.connect(self.path) as c:
cur = c.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
return cur.rowcount > 0


def list_rules(self) -> List[Dict[str, Any]]:
with sqlite3.connect(self.path) as c:
cur = c.execute("SELECT id, kind, payload FROM rules ORDER BY id ASC")
rows = cur.fetchall()
out = []
for rid, kind, payload in rows:
data = json.loads(payload)
out.append({"id": rid, "kind": kind, **data})
return out


# ===== settings =====
def get(self, key: str) -> Optional[str]:
with sqlite3.connect(self.path) as c:
cur = c.execute("SELECT value FROM settings WHERE key = ?", (key,))
row = cur.fetchone()
return row[0] if row else None


def set(self, key: str, value: str) -> None:
with sqlite3.connect(self.path) as c:
c.execute("REPLACE INTO settings(key, value) VALUES(?,?)", (key, value))
