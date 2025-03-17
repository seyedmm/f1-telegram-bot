import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from os import getenv
from aioclock import AioClock, Every
from dotenv import load_dotenv
from models import TelegramUpdateBot
load_dotenv()

tg_bot = TelegramUpdateBot(chat_id=getenv("CHAT_ID"))

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")

@asynccontextmanager
async def lifespan(app: AioClock):
    global tg_bot
    logging.info("Startin the robot")
    tg_bot.fetch_session_and_drivers()
    tg_bot.send_new_message()
    logging.info("Started the robot")
    yield app
    tg_bot.tg_logout()

app = AioClock(lifespan=lifespan)

@app.task(trigger=Every(seconds=5))
async def update_message():
    global tg_bot
    if datetime.now(timezone.utc) < tg_bot.current_session['date_end']:
        tg_bot.fetch_session_and_drivers()
        tg_bot.fetch_new_positions()
    tg_bot.update_message(tg_bot.pretty_data())
    logging.debug("Updating message")

@app.task(trigger=Every(minutes=20))
async def new_message():
    global tg_bot
    logging.info("Sending a new message")
    tg_bot.send_new_message()

if __name__ == "__main__":
    asyncio.run(app.serve())
