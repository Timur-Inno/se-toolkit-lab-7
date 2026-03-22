import sys
import json
import urllib.request
import urllib.error
from config import settings

TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "List all labs and tasks in the system", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_learners", "description": "List enrolled students and their groups", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution (4 buckets) for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID e.g. lab-04"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task average scores and attempt counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID e.g. lab-04"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions per day for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID e.g. lab-04"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group scores and student counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID e.g. lab-04"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners by score for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}, "limit": {"type": "integer", "description": "Number of top learners to return"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate percentage for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Refresh/sync data from the autochecker", "parameters": {"type": "object", "properties": {}}}},
]

SYSTEM_PROMPT = """You are an LMS assistant bot. Answer user questions about labs, scores, and learners using the available tools.
Always call tools to get real data before answering. Do not make up numbers.
For multi-lab comparisons, call the relevant tool for each lab.
Be concise and format answers clearly."""

def call_llm(messages: list) -> dict:
    payload = json.dumps({
        "model": settings.llm_api_model,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto"
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_api_base_url}/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {settings.llm_api_key}"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())

def execute_tool(name: str, args: dict) -> str:
    from services.lms_client import get
    import httpx
    from config import settings as s
    try:
        if name == "get_items": return json.dumps(get("/items/"))
        elif name == "get_learners": return json.dumps(get("/learners/"))
        elif name == "get_scores": return json.dumps(get(f"/analytics/scores?lab={args['lab']}"))
        elif name == "get_pass_rates": return json.dumps(get(f"/analytics/pass-rates?lab={args['lab']}"))
        elif name == "get_timeline": return json.dumps(get(f"/analytics/timeline?lab={args['lab']}"))
        elif name == "get_groups": return json.dumps(get(f"/analytics/groups?lab={args['lab']}"))
        elif name == "get_top_learners": return json.dumps(get(f"/analytics/top-learners?lab={args['lab']}&limit={args.get('limit', 5)}"))
        elif name == "get_completion_rate": return json.dumps(get(f"/analytics/completion-rate?lab={args['lab']}"))
        elif name == "trigger_sync":
            r = httpx.post(f"{s.lms_api_base_url}/pipeline/sync", headers={"Authorization": f"Bearer {s.lms_api_key}"}, timeout=30)
            return json.dumps(r.json())
        else: return "Unknown tool"
    except Exception as e:
        return f"Error: {e}"

def route(user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    for _ in range(10):
        data = call_llm(messages)
        msg = data["choices"][0]["message"]
        messages.append(msg)
        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                print(f"[tool] LLM called: {fn}({args})", file=sys.stderr)
                result = execute_tool(fn, args)
                print(f"[tool] Result: {result[:100]}", file=sys.stderr)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
            print(f"[summary] Feeding {len(msg['tool_calls'])} tool result(s) back to LLM", file=sys.stderr)
        else:
            return (msg.get("content") or "I couldn't generate a response.")
    return "Reached maximum tool calls."
