import sqlite3


class DB:
    def __init__(self, path):
        self.path = path
        self.init()

    def init(self):
        with sqlite3.connect(self.path) as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)

    def add_phrase(self, phrase: str):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT INTO rules (type, content) VALUES (?, ?)", ("phrase", phrase))
            c.commit()

    def add_allwords(self, words: str):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT INTO rules (type, content) VALUES (?, ?)", ("allwords", words))
            c.commit()

    def list_rules(self):
        with sqlite3.connect(self.path) as c:
            return c.execute("SELECT id, type, content FROM rules").fetchall()

    def del_rule(self, rule_id: int):
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            c.commit()
