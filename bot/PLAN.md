# Bot Development Plan

## Architecture
The bot uses a layered architecture to keep handlers testable without Telegram:
- `bot.py` — entry point, handles Telegram startup and `--test` mode
- `handlers/` — pure functions that process commands and return text strings
- `services/` — API client for backend, LLM client for intent routing
- `config.py` — loads env vars from `.env.bot.secret`

## Task 1: Scaffold
Create the project structure with `--test` mode. Handlers return placeholder text. Verify with `uv run bot.py --test "/start"`.

## Task 2: Backend Integration
Implement `/health`, `/scores`, `/labs`, `/items` using real API calls to the LMS backend via `services/lms_client.py`.

## Task 3: Intent Routing
Add natural language understanding using the LLM (Qwen). User messages are routed to the right handler based on intent detected by the LLM.

## Task 4: Containerize
Add bot to `docker-compose.yml`, write `Dockerfile` for bot, document deployment steps in `AGENT.md`.

## Testing Strategy
Use `--test` mode for all commands before deploying to Telegram. Each handler is a plain function — easy to unit test without mocking Telegram.
