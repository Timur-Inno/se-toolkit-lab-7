import sys
import asyncio

def run_test(command: str) -> None:
    from handlers.commands import (
        handle_start, handle_help, handle_health, handle_labs,
        handle_scores, handle_unknown, handle_nl
    )
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/start": print(handle_start())
    elif cmd == "/help": print(handle_help())
    elif cmd == "/health": print(handle_health())
    elif cmd == "/labs": print(handle_labs())
    elif cmd == "/scores": print(handle_scores(args))
    elif cmd.startswith("/"): print(handle_unknown(cmd))
    else: print(handle_nl(command))

async def run_bot() -> None:
    from aiogram import Bot, Dispatcher, F
    from aiogram.filters import Command
    from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
    from handlers.commands import (
        handle_start, handle_help, handle_health, handle_labs,
        handle_scores, handle_unknown, handle_nl
    )
    from config import settings

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    start_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 List Labs", callback_data="labs"),
         InlineKeyboardButton(text="❤️ Health Check", callback_data="health")],
        [InlineKeyboardButton(text="📊 Scores lab-04", callback_data="scores_lab-04")]
    ])

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(handle_start(), reply_markup=start_kb)

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

    from aiogram.types import CallbackQuery
    @dp.callback_query()
    async def handle_callback(callback: CallbackQuery) -> None:
        data = callback.data or ""
        if data == "labs": text = handle_labs()
        elif data == "health": text = handle_health()
        elif data.startswith("scores_"): text = handle_scores(data[7:])
        else: text = "Unknown action"
        await callback.message.answer(text)
        await callback.answer()

    @dp.message(F.text)
    async def nl_message(message: Message) -> None:
        text = message.text or ""
        if text.startswith("/"):
            await message.answer(handle_unknown(text.split()[0]))
        else:
            await message.answer(handle_nl(text))

    await dp.start_polling(bot)

if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/help"
        run_test(command)
    else:
        asyncio.run(run_bot())
