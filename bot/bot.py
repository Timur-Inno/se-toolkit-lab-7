import sys
import asyncio

def run_test(command: str) -> None:
    from handlers.commands import (
        handle_start, handle_help, handle_health, handle_labs, handle_scores
    )
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/start":
        print(handle_start())
    elif cmd == "/help":
        print(handle_help())
    elif cmd == "/health":
        print(handle_health())
    elif cmd == "/labs":
        print(handle_labs())
    elif cmd == "/scores":
        print(handle_scores(args))
    else:
        print(f"Unknown command: {cmd}")

async def run_bot() -> None:
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command
    from aiogram.types import Message
    from handlers.commands import (
        handle_start, handle_help, handle_health, handle_labs, handle_scores
    )
    from config import settings

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(handle_start())

    @dp.message(Command("help"))
    async def help(message: Message) -> None:
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def health(message: Message) -> None:
        await message.answer(handle_health())

    @dp.message(Command("labs"))
    async def labs(message: Message) -> None:
        await message.answer(handle_labs())

    @dp.message(Command("scores"))
    async def scores(message: Message, command) -> None:
        await message.answer(handle_scores(command.args or ""))

    await dp.start_polling(bot)

if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/help"
        run_test(command)
    else:
        asyncio.run(run_bot())
