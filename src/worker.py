"""
ScholarAI - Cloudflare Python Worker
Correct entrypoint: WorkerEntrypoint class with async fetch() method.
Uses JS interop (from js import ...) for Response, Headers, URL.
"""

import json
from js import Response, Headers, URL
from pyodide.ffi import to_js
from workers import WorkerEntrypoint


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
AI_MODEL   = "@cf/meta/llama-3.1-8b-instruct"
MAX_TOKENS = 1024


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def _headers(content_type: str = "application/json") -> Headers:
    h = Headers.new()
    h.set("Content-Type", content_type)
    h.set("Access-Control-Allow-Origin",  "*")
    h.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    h.set("Access-Control-Allow-Headers", "Content-Type")
    return h


def json_resp(data: dict, status: int = 200) -> Response:
    return Response.new(
        json.dumps(data),
        to_js({"status": status, "headers": {"Content-Type": "application/json",
               "Access-Control-Allow-Origin": "*"}}),
    )


def error_resp(message: str, status: int = 400) -> Response:
    return json_resp({"ok": False, "error": message}, status)


def html_resp(html: str) -> Response:
    return Response.new(
        html,
        to_js({"status": 200, "headers": {"Content-Type": "text/html; charset=utf-8"}}),
    )


def cors_resp() -> Response:
    return Response.new(
        "",
        to_js({
            "status": 204,
            "headers": {
                "Access-Control-Allow-Origin":  "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        }),
    )


# ---------------------------------------------------------------------------
# AI helper
# ---------------------------------------------------------------------------

async def run_ai(env, system_prompt: str, user_prompt: str) -> str:
    payload = to_js({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens": MAX_TOKENS,
    })
    result = await env.AI.run(AI_MODEL, payload)
    text = getattr(result, "response", None)
    if text is None:
        text = str(result)
    return text.strip()


# ---------------------------------------------------------------------------
# Body parser
# ---------------------------------------------------------------------------

async def parse_body(request) -> dict:
    try:
        text = await request.text()
        return json.loads(text) if text else {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# HTML — served via ASSETS binding
# ---------------------------------------------------------------------------

_HTML_CACHE: str | None = None


async def get_html(env) -> str:
    global _HTML_CACHE
    if _HTML_CACHE:
        return _HTML_CACHE
    try:
        resp = await env.ASSETS.fetch("http://assets/index.html")
        _HTML_CACHE = await resp.text()
        return _HTML_CACHE
    except Exception as e:
        return (
            "<!doctype html><html><body>"
            "<h1>ScholarAI</h1>"
            f"<p>Frontend load error: {e}</p>"
            "</body></html>"
        )


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

async def handle_health(request, env) -> Response:
    return json_resp({"ok": True, "service": "scholarai", "model": AI_MODEL})


async def handle_ask(request, env) -> Response:
    body     = await parse_body(request)
    question = str(body.get("question") or "").strip()
    context  = str(body.get("context")  or "").strip()

    if not question:
        return error_resp("'question' is required.")

    system_prompt = (
        "You are ScholarAI, an expert academic research assistant. "
        "Answer research questions clearly and accurately. "
        "If paper context is provided, base your answer on it. "
        "If unsure, say so rather than guessing."
    )
    ctx_block   = f"\n\nContext from uploaded paper:\n{context[:10000]}" if context else ""
    user_prompt = f"Question: {question}{ctx_block}"

    try:
        answer = await run_ai(env, system_prompt, user_prompt)
        return json_resp({"ok": True, "answer": answer})
    except Exception as e:
        return error_resp(f"AI error: {e}", 500)


async def handle_summarize(request, env) -> Response:
    body     = await parse_body(request)
    title    = str(body.get("title")    or "").strip()
    abstract = str(body.get("abstract") or "").strip()
    content  = str(body.get("content")  or "").strip()

    if not (title or abstract or content):
        return error_resp("At least one of 'title', 'abstract', or 'content' is required.")

    parts = []
    if title:    parts.append(f"Title: {title}")
    if abstract: parts.append(f"Abstract: {abstract}")
    if content:  parts.append(f"Content:\n{content[:10000]}")

    system_prompt = (
        "You are ScholarAI, an expert at summarising research papers. "
        "Produce a structured summary: main contribution, problem, "
        "methodology, key findings, and significance."
    )
    user_prompt = "Summarise this paper:\n\n" + "\n\n".join(parts)

    try:
        summary = await run_ai(env, system_prompt, user_prompt)
        return json_resp({"ok": True, "title": title, "summary": summary})
    except Exception as e:
        return error_resp(f"AI error: {e}", 500)


async def handle_discover(request, env) -> Response:
    body   = await parse_body(request)
    query  = str(body.get("query") or "").strip()
    fields = body.get("fields") or []
    limit  = int(body.get("limit") or 10)

    if not query:
        return error_resp("'query' is required.")

    field_ctx     = f" in the fields of {', '.join(fields)}" if fields else ""
    system_prompt = (
        "You are ScholarAI, an expert academic research assistant. "
        "Suggest relevant papers, key concepts, and research directions."
    )
    user_prompt = (
        f"Suggest up to {limit} relevant academic papers{field_ctx} for:\n\n"
        f"Query: {query}\n\n"
        "For each paper: title, likely authors/year, one-line relevance. "
        "Then list 3-5 key concepts and 2-3 related queries."
    )

    try:
        results = await run_ai(env, system_prompt, user_prompt)
        return json_resp({"ok": True, "query": query, "results": results})
    except Exception as e:
        return error_resp(f"AI error: {e}", 500)


async def handle_review(request, env) -> Response:
    body     = await parse_body(request)
    topic    = str(body.get("topic")    or "").strip()
    style    = str(body.get("style")    or "comprehensive").strip()
    audience = str(body.get("audience") or "researchers").strip()
    context  = str(body.get("context")  or "").strip()

    if not topic:
        return error_resp("'topic' is required.")

    ctx_block     = f"\n\nPaper content for reference:\n{context[:10000]}" if context else ""
    system_prompt = (
        "You are ScholarAI, an expert at writing academic literature reviews. "
        "Generate well-structured, rigorous literature reviews."
    )
    user_prompt = (
        f"Write a {style} literature review on '{topic}' for {audience}.{ctx_block}\n\n"
        "Structure: Introduction, Background, State of the Art, "
        "Key Methodologies, Major Findings, Open Challenges, Future Directions."
    )

    try:
        review = await run_ai(env, system_prompt, user_prompt)
        return json_resp({"ok": True, "topic": topic, "style": style, "review": review})
    except Exception as e:
        return error_resp(f"AI error: {e}", 500)


# ---------------------------------------------------------------------------
# Router table
# ---------------------------------------------------------------------------

ROUTES = {
    "GET /api/health":     handle_health,
    "POST /api/ask":       handle_ask,
    "POST /api/summarize": handle_summarize,
    "POST /api/discover":  handle_discover,
    "POST /api/review":    handle_review,
}


# ---------------------------------------------------------------------------
# Entrypoint — MUST be a WorkerEntrypoint subclass with async fetch()
# Cloudflare Python Workers require this exact pattern.
# ---------------------------------------------------------------------------

class Default(WorkerEntrypoint):

    async def fetch(self, request) -> Response:
        method = request.method.upper()
        path   = URL.new(str(request.url)).pathname

        # CORS preflight
        if method == "OPTIONS":
            return cors_resp()

        # Serve HTML for root path
        if method == "GET" and path in ("/", "/index.html"):
            return html_resp(await get_html(self.env))

        # API routes
        handler = ROUTES.get(f"{method} {path}")
        if handler is None:
            return error_resp(f"Not found: {method} {path}", 404)

        return await handler(request, self.env)