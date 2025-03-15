import json
import requests
import util
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
load_dotenv()

chat_id = 1213079698
msg_id = 3
current_session = util.get_last_session()
DRIVER_LIST = util.session_driver_list(current_session['session_key'])
