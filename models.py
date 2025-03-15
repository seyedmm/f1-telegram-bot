import requests
import json
import util
from util import TG_BASE_URL as BASE_URL
from datetime import datetime


class TelegramUpdateBot:
    def __init__(self, chat_id: int):
        self.chat_id=chat_id
        self.current_message_id=None
        self.last_new_message_time=0
        self.last_update_time=datetime(1,1,1)
        self.next_update_time=datetime(1,1,1)
        self.current_session={}
        self.driver_list=[]
        self.position_list=[]

    def update_message(self):
        text = self.pretty_data()
        resp = requests.get(BASE_URL+f"editMessageText?chat_id={self.chat_id}&message_id={self.current_message_id}&text={text}", proxies=util.PROXIES)
        self.last_update_time = datetime.now()
        return json.loads(resp.text)

    def send_new_message(self):
        text = self.pretty_data()
        resp = requests.get(BASE_URL+f"sendMessage?chat_id={self.chat_id}&text={text}", proxies=util.PROXIES)
        return json.loads(resp.text)

    def fetch_session_and_drivers(self):
        self.current_session_key = util.get_last_session()
        self.driver_list = util.session_driver_list(self.current_session['session_key'])
        self.last_update_time = datetime.now()

    def pretty_data(self) -> str:
        output = "موقعیت های رانندگان:\n"
        for pos in sorted(self.position_list, key=lambda pos: pos['position']):
            output += str(pos['position'])+": "+pos['driver']['name_acronym']+str(pos['driver']['driver_number'])+"\n"
        output += "آخرین بروزرسانی: "+self.last_update_time.strftime("%H:%M:%S")
        return output
    
    
