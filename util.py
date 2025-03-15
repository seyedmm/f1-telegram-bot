import dateutil
import json
import requests
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
load_dotenv()

PROXIES = {"http":"http://127.0.0.1:2080",
           "https":"http://127.0.0.1:2080"}
BASE_URL="https://api.openf1.org/v1/"
TG_BASE_URL = f"https://api.telegram.org/bot{getenv("TG_TOKEN")}/"


def session_driver_list(session_key: int) -> list[dict]:
        """
        Returns a list of drivers.
        """
        resp = requests.get(BASE_URL+f"drivers?session_key={session_key}", proxies=PROXIES)
        return json.loads(resp.text)


def get_driver_position(driver_number:int, session_key:int):
    """
    Returns last position of a driver in a session
    """
    resp = requests.get(BASE_URL+f"position?session_key={session_key}&driver_number={driver_number}", proxies=PROXIES)
    return sorted(json.loads(resp.text), key=lambda pos: pos["date"])[-1]["position"]

def get_all_drivers_positions(session_key:int, driver_list:list[dict]):
    """Returns any postion that any driver had in a session"""
    resp = requests.get(BASE_URL+f"position?session_key={session_key}", proxies=PROXIES)
    pos_list = json.loads(resp.text)

    # Updating position objects with more usable data
    for pos in pos_list:
        pos["date"] = dateutil.parser.parse(pos["date"])
        driver = list(filter(lambda d: d['driver_number']==pos['driver_number'],driver_list))
        pos["driver"] = driver[0] 
    return pos_list


def get_last_drivers_position(session_key:int, driver_list: list[dict]):
    # Returns last position all drivers had in a session
    pos_list = get_all_drivers_positions(session_key, driver_list)
    pos_dict = {}
    for item in pos_list:
        #pos_dict[pos['driver_number']] = pos['position']
        position = item["position"]
        date = item["date"]
    
        # If we haven't seen this position yet, or if this date is later than what we've seen
        if position not in pos_dict or date > pos_dict[position]["date"]:
            pos_dict[position] = item
    return list(pos_dict.values())


def get_last_session(year:int=datetime.now().year):
    resp = requests.get(BASE_URL+f"sessions?year={year}", proxies=PROXIES)
    return sorted(json.loads(resp.text), key=(lambda ses: dateutil.parser.parse(ses["date_start"])))[-1]
