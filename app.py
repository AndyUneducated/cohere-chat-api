import json
import logging
import os
import time

import cohere
from dotenv import load_dotenv
from flask import Flask, jsonify, request

import history
import wikipedia

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))
MODEL = "command-a-03-2025"

RATE_LIMIT = 10
_hits = {}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "wikipedia_search",
            "description": "Search Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    }
]

history.init_db()


def check_rate_limit(ip):
    now = time.time()
    arr = _hits.get(ip, [])
    arr = [t for t in arr if now - t < 60]
    if len(arr) >= RATE_LIMIT:
        _hits[ip] = arr
        return False
    arr.append(now)
    _hits[ip] = arr
    return True


def run_chat(query):
    msgs = [{"role": "user", "content": query}]
    used_wiki = False

    for i in range(3):
        resp = co.chat(model=MODEL, messages=msgs, tools=TOOLS)
        msg = resp.message

        if not msg.tool_calls:
            if msg.content:
                return msg.content[0].text, used_wiki
            return "", used_wiki

        msgs.append(msg)

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)

            if name == "wikipedia_search":
                q = args.get("query", query)
                print("calling wiki:", q)
                used_wiki = True
                try:
                    results = wikipedia.search(q)
                except Exception as e:
                    logging.warning("wiki error: %s", e)
                    results = []
            else:
                results = []

            if results:
                content = []
                for r in results:
                    content.append({"type": "document", "document": {"data": json.dumps(r)}})
            else:
                content = "no result from wiki"

            msgs.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": content,
            })

    # fallback
    resp = co.chat(model=MODEL, messages=msgs)
    if resp.message.content:
        return resp.message.content[0].text, used_wiki
    return "", used_wiki


@app.route("/chat", methods=["POST"])
def chat():
    ip = request.remote_addr or "0.0.0.0"
    if not check_rate_limit(ip):
        return jsonify({"error": "too many requests"}), 429

    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400

    try:
        answer, used_wiki = run_chat(query)
    except Exception as e:
        logging.exception("failed")
        return jsonify({"error": str(e)}), 500

    history.add(query, answer, used_wiki)
    return jsonify({"query": query, "response": answer, "used_wikipedia": used_wiki})


@app.route("/history", methods=["GET"])
def get_history():
    return jsonify({"history": history.list_all()})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
