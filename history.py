import sqlite3

DB = "chat_history.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS history ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id TEXT, query TEXT, response TEXT, used_wikipedia INTEGER)"
    )
    # if old table has no user_id column
    try:
        conn.execute("ALTER TABLE history ADD COLUMN user_id TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()


def add(user_id, query, response, used_wikipedia=False):
    conn = sqlite3.connect(DB)
    flag = 1 if used_wikipedia else 0
    conn.execute(
        "INSERT INTO history (user_id, query, response, used_wikipedia) VALUES (?, ?, ?, ?)",
        (user_id, query, response, flag),
    )
    conn.commit()
    conn.close()


def list_for_user(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "SELECT query, response, used_wikipedia FROM history "
        "WHERE user_id = ? ORDER BY id",
        (user_id,),
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
