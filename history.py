import sqlite3

DB = "chat_history.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS history ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "query TEXT, response TEXT, used_wikipedia INTEGER)"
    )
    conn.commit()
    conn.close()


def add(query, response, used_wikipedia=False):
    conn = sqlite3.connect(DB)
    flag = 1 if used_wikipedia else 0
    conn.execute(
        "INSERT INTO history (query, response, used_wikipedia) VALUES (?, ?, ?)",
        (query, response, flag),
    )
    conn.commit()
    conn.close()


def list_all():
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "SELECT query, response, used_wikipedia FROM history ORDER BY id"
    )
    items = []
    for row in cur.fetchall():
        items.append({
            "query": row[0],
            "response": row[1],
            "used_wikipedia": bool(row[2]),
        })
    conn.close()
    return items

# for tests
def clear():
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
