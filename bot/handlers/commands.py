def handle_start() -> str:
    return "Welcome to the LMS Bot! Use /help to see available commands."

def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Per-task pass rates for a lab"
    )

def handle_health() -> str:
    try:
        from services.lms_client import get
        items = get("/items/")
        return f"Backend is healthy. {len(items)} items available."
    except RuntimeError as e:
        return f"Backend error: {e}"

def handle_labs() -> str:
    try:
        from services.lms_client import get
        items = get("/items/")
        labs = [i for i in items if i.get("type") == "lab"]
        if not labs:
            return "No labs found."
        lines = "\n".join(f"- {lab['title']}" for lab in labs)
        return f"Available labs:\n{lines}"
    except RuntimeError as e:
        return f"Backend error: {e}"

def handle_scores(args: str = "") -> str:
    lab = args.strip()
    if not lab:
        return "Usage: /scores <lab-id>  Example: /scores lab-04"
    try:
        from services.lms_client import get
        data = get(f"/analytics/pass-rates?lab={lab}")
        if not data:
            return f"No data found for {lab}. Check the lab ID."
        lines = "\n".join(
            f"- {r['task']}: {r['avg_score']:.1f}% ({r.get('attempts', '?')} attempts)"
            for r in data
        )
        return f"Pass rates for {lab}:\n{lines}"
    except RuntimeError as e:
        return f"Backend error: {e}"

def handle_unknown(cmd: str) -> str:
    return f"Unknown command: {cmd}. Use /help to see available commands."
