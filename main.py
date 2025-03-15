import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from os import getenv
from aioclock import AioClock, Every
from dotenv import load_dotenv
from models import TelegramUpdateBot
load_dotenv()

tg_bot = TelegramUpdateBot(chat_id=getenv("CHAT_ID"))

@asynccontextmanager
async def lifespan(app: AioClock):
    global tg_bot
    print("startup")
    tg_bot.fetch_session_and_drivers()
    tg_bot.send_new_message()
    yield app
    tg_bot.tg_logout()

app = AioClock(lifespan=lifespan)

@app.task(trigger=Every(seconds=5))
async def update_message():
    global tg_bot
    print(datetime.now().strftime("%H:%M:%S"),"Updating")
    tg_bot.fetch_new_positions()
    tg_bot.update_message(tg_bot.pretty_data())

@app.task(trigger=Every(minutes=20))
async def new_message():
    global tg_bot
    tg_bot.fetch_session_and_drivers()
    tg_bot.send_new_message()

asyncio.run(app.serve())
