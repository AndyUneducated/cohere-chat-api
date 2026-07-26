import history
import app as myapp

history.init_db()
c = myapp.app.test_client()


def setup_function():
    history.clear()
    myapp._hits.clear()
    myapp.RATE_LIMIT = 10


def test_empty():
    assert c.post("/chat", json={"query": ""}).status_code == 400


def test_no_json():
    # i forgot content-type once
    assert c.post("/chat").status_code == 400


def test_ok(monkeypatch):
    monkeypatch.setattr(myapp, "run_chat", lambda q: ("ok", True))
    r = c.post("/chat", json={"query": "moon?", "user": "ann"})
    j = r.get_json()
    assert r.status_code == 200
    assert j["user"] == "ann"
    assert j["used_wikipedia"]

    hist = c.get("/history?user=ann").get_json()["history"]
    assert hist[0]["query"] == "moon?"


def test_two_users(monkeypatch):
    monkeypatch.setattr(myapp, "run_chat", lambda q: ("x", False))
    c.post("/chat", json={"query": "q1", "user": "1"})
    c.post("/chat", json={"query": "q2", "user": "2"})
    c.post("/chat", json={"query": "q3", "user": "1"})

    u1 = c.get("/history?user=1").get_json()["history"]
    u2 = c.get("/history?user=2").get_json()["history"]
    assert len(u1) == 2
    assert len(u2) == 1


def test_fail(monkeypatch):
    def bad(q):
        raise Exception("down")
    monkeypatch.setattr(myapp, "run_chat", bad)
    assert c.post("/chat", json={"query": "hi"}).status_code == 500


def test_rate(monkeypatch):
    myapp.RATE_LIMIT = 2
    monkeypatch.setattr(myapp, "run_chat", lambda q: ("ok", False))
    c.post("/chat", json={"query": "1"})
    c.post("/chat", json={"query": "2"})
    assert c.post("/chat", json={"query": "3"}).status_code == 429
