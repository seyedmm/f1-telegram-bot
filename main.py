import json
import requests
import util
import time
from os import getenv
from dotenv import load_dotenv
load_dotenv()

start_time = time.time()
chat_id = 1213079698
msg_id = 3
BASE_URL = f"https://api.telegram.org/bot{getenv("TG_TOKEN")}/"
current_session = util.get_last_session()
DRIVER_LIST = util.session_driver_list(current_session['session_key'])

class TelegramUpdateBot:
    def __init__(self, chat_id: int):
        self.chat_id=chat_id
        self.current_message_id=None
        self.last_new_message_time=0
        self.last_update_time=0
        self.current_session={}
        self.driver_list=[]
        self.position_list=[]

    def update_message(self):
        resp = requests.get(BASE_URL+f"updateMessage?chat_id={self.chat_id}&message_id={self.current_message_id}&text={util.pretty_output(self.position_list)}", proxies=util.PROXIES)
        return json.loads(resp.text)

    def fetch_session_and_drivers(self):
        self.current_session_key = util.get_last_session()
        self.driver_list = util.session_driver_list(self.current_session['session_key'])

