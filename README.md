# Cohere Chat API (with Wikipedia)

You send a question, it calls Cohere chat. If the model wants Wikipedia info, we search wiki and call Cohere again. History is saved in sqlite.

## Get started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

example usages:

```bash
bash curl_examples.sh
```

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the 2 person to walk on the moon?"}'

curl http://127.0.0.1:5000/history
```

/chat also returns "used_wikipedia" so you can see if wiki tool was used.

tests:

```bash
pytest -q
```

## Design decisions and limits

I used Flask because it is simple and enough for 2 endpoints.

- `app.py`: HTTP routes, Cohere call, tool loop, rate limit
- `wikipedia.py`: Wikipedia search
- `history.py`: sqlite save / load

English Wikipedia only, srlimit=5. Wiki request has a timeout. The model may not always call the tool.

I only loop tool calls a few times so it will not hang forever.

There is a very simple rate limit (per IP). No real auth.

Basic logging to stdout. If wiki fails we log a warning and continue (model can still answer). Cohere errors return 500.

## Trade-offs

- sqlite file is easy, but not good for multi-server deploy
- rate limit is in memory, so it resets when process restarts
- model decides when to use the tool. i don't force it for every question
- keeping cohere + tool loop in app.py is a bit mixed, but ok for this size

## What I would change before real users

- Auth / API key
- Cache Wikipedia results
- Use real production server
- Per-user history, not one shared table
- Support more languages, not only English
- Better rate limit (redis)

## Resources

- Cohere API: https://docs.cohere.com/v2/reference/chat
- Cohere tool: https://docs.cohere.com/v2/docs/tool-use-overview
- MediaWiki: https://www.mediawiki.org/wiki/API:Search
- Flask & Cohere python docs
