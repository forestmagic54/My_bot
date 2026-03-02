import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MY_USER_ID = 5204660456
expenses = {}
bot = Bot(token = TOKEN)
dp = Dispatcher()

async def on_startup() -> None:
    webhook_url = f"https://{os.environ['USERNAME']}.pythonanywhere.com/webhook"
    await bot.set_webhook(webhook_url, allowed_updates=dp.resolve_used_update_types())
    print(f"Бот запущен, вебхук установлен на {webhook_url}")

async def on_shutdown() -> None:
    await bot.delete_webhook()

app = web.Application()
webhook_requests_handler = SimpleRequestHandler(
    dispatcher = dp,
    bot = bot
)
webhook_requests_handler.register(app, path = "/webhook")
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

@dp.message(Command("start"))
async def start_message(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if user_id not in expenses:
        expenses[user_id] = {}

    await message.answer(
        f"Привет, {user_name}!\n\n"
        "Я помогаю учитывать расходы\n"
        "Команды:\n"
        "/add - добавить расход\n"
        "/stats - статистика\n"
        "/reset - сбросить всё"
    )

@dp.message(Command("add"))
async def add_command(message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in expenses:
        expenses[user_id] = {}

    parts = text.split()
    if len(parts) != 3:
        await message.answer("Неправильный ввод")

    try:
        amount = int(parts[1])
        category = parts[2].lower()

        if category in expenses[user_id]:
            expenses[user_id][category] += amount
        else:
            expenses[user_id][category] = amount

        await message.answer(f"Добавлено: {amount} рублей в категорию {category}")

    except ValueError:
        await message.answer("Сумма должна быть числом")

@dp.message(Command("stats"))
async def show_stats(message):
    user_id = message.from_user.id

    if user_id not in expenses or not expenses[user_id]:
        await message.answer("У тебя пока нет трат")

    total = sum(expenses[user_id].values())
    text = f"Всего расходов: {total}"

    await message.answer(text)




async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())