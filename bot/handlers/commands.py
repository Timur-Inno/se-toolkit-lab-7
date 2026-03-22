def handle_start() -> str:
    return "Welcome to the LMS Bot! Use /help to see available commands."

def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Show scores for a lab"
    )

def handle_health() -> str:
    return "Backend status: checking... (not yet implemented)"

def handle_labs() -> str:
    return "Labs: (not yet implemented)"

def handle_scores(args: str = "") -> str:
    return f"Scores for {args or 'all labs'}: (not yet implemented)"
