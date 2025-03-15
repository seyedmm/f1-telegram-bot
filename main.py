import asyncio
from os import getenv
from aioclock import AioClock, Depends, Every
from dotenv import load_dotenv
from models import TelegramUpdateBot
load_dotenv()

tg_bot = TelegramUpdateBot(chat_id=int(getenv("CHAT_ID")))
app = AioClock()

def return_tg_bot():
    global tg_bot
    return tg_bot


asyncio.run(app.serve())
