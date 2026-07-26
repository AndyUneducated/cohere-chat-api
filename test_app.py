import history
import app as myapp

history.init_db()
client = myapp.app.test_client()

def setup_function():
    history.clear()
    myapp._hits.clear()
    myapp.RATE_LIMIT = 10


def test_empty():
    r = client.post("/chat", json={"query": ""})
    assert r.status_code == 400


def test_no_body():
    # forgot to send json
    r = client.post("/chat")
    assert r.status_code == 400


def test_history(monkeypatch):
    monkeypatch.setattr(myapp, "run_chat", lambda q: ("ok", True))

    r = client.post("/chat", json={"query": "moon?"})
    data = r.get_json()
    assert r.status_code == 200
    assert data["used_wikipedia"] is True

    h = client.get("/history").get_json()["history"]
    assert h[0]["query"] == "moon?"


def test_history_grows(monkeypatch):
    monkeypatch.setattr(myapp, "run_chat", lambda q: ("ans", False))
    client.post("/chat", json={"query": "a"})
    client.post("/chat", json={"query": "b"})
    h = client.get("/history").get_json()["history"]
    assert len(h) == 2


def test_error(monkeypatch):
    def boom(q):
        raise RuntimeError("cohere down")

    monkeypatch.setattr(myapp, "run_chat", boom)
    r = client.post("/chat", json={"query": "hi"})
    assert r.status_code == 500


def test_rate_limit(monkeypatch):
    myapp.RATE_LIMIT = 2
    monkeypatch.setattr(myapp, "run_chat", lambda q: ("ok", False))

    client.post("/chat", json={"query": "1"})
    client.post("/chat", json={"query": "1"})
    r = client.post("/chat", json={"query": "1"})
    assert r.status_code == 429


def test_wiki():
    # just make sure wiki helper works (needs network)
    res = myapp.wikipedia.search("Buzz Aldrin")
    assert isinstance(res, list)
    assert len(res) > 0
    assert "title" in res[0]
