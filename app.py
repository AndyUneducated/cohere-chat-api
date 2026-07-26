import json, logging, os, time
import cohere
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import history, wikipedia

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))
MODEL = "command-a-03-2025"
RATE_LIMIT = 10
_hits = {}

# cohere tool schema
TOOLS = [{"type": "function", "function": {
    "name": "wikipedia_search",
    "description": "search wiki",
    "parameters": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}}]

history.init_db()


def check_rate_limit(ip):
    now = time.time()
    old = [t for t in _hits.get(ip, []) if now - t < 60]
    if len(old) >= RATE_LIMIT:
        _hits[ip] = old
        return False
    old.append(now)
    _hits[ip] = old
    return True


def run_chat(query):
    msgs = [{"role": "user", "content": query}]
    used_wiki = False

    for _ in range(3):
        resp = co.chat(model=MODEL, messages=msgs, tools=TOOLS)
        m = resp.message
        if not m.tool_calls:
            txt = m.content[0].text if m.content else ""
            return txt, used_wiki

        msgs.append(m)
        for tc in m.tool_calls:
            args = json.loads(tc.function.arguments)
            results = []
            if tc.function.name == "wikipedia_search":
                q = args.get("query") or query
                print("calling wiki:", q)
                used_wiki = True
                try:
                    results = wikipedia.search(q)
                except Exception as e:
                    print("wiki fail", e)

            if results:
                content = [{"type": "document", "document": {"data": json.dumps(x)}} for x in results]
            else:
                content = "no wiki result"

            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": content})

    resp = co.chat(model=MODEL, messages=msgs)
    txt = resp.message.content[0].text if resp.message.content else ""
    return txt, used_wiki


@app.route("/chat", methods=["POST"])
def chat():
    ip = request.remote_addr or "0.0.0.0"
    if not check_rate_limit(ip):
        return jsonify({"error": "too many requests"}), 429

    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400

    user = body.get("user") or "default"
    user = str(user).strip() or "default"

    try:
        answer, used_wiki = run_chat(query)
    except Exception as e:
        logging.exception("chat error")
        return jsonify({"error": str(e)}), 500

    history.add(user, query, answer, used_wiki)
    return jsonify({
        "user": user,
        "query": query,
        "response": answer,
        "used_wikipedia": used_wiki,
    })


@app.route("/history", methods=["GET"])
def get_history():
    user = request.args.get("user") or "default"
    user = str(user).strip() or "default"
    return jsonify({"user": user, "history": history.list_for_user(user)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
