from typing import Any
import dateutil
import json
import requests
from requests.models import Response

proxies = {"http":"http://127.0.0.1:2080",
           "https":"http://127.0.0.1:2080"}
BASE_URL="https://api.openf1.org/v1/"


def session_driver_list(session_key: int) -> list[dict]:
        """
        Returns a list of drivers.
        """
        resp = requests.get(BASE_URL+f"drivers?session_key={session_key}", proxies=proxies)
        return json.loads(resp.text)


def get_driver_position(driver_number:int, session_key:int):
    """
    Returns last position of a driver in a session
    """
    resp = requests.get(BASE_URL+f"position?session_key={session_key}&driver_number={driver_number}", proxies=proxies)
    return sorted(json.loads(resp.text), key=lambda pos: pos["date"])[-1]["position"]

def get_all_drivers_positions(session_key:int, driver_list:list[dict]):
    """Returns any postion that any driver had in a session"""
    resp = requests.get(BASE_URL+f"position?session_key={session_key}", proxies=proxies)
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
    sorted_pos_list = sorted(pos_list, key=lambda pos: pos["date"])
    pos_dict = {}
    for pos in sorted_pos_list:
        pos_dict[pos['driver_number']] = pos['position']
    return pos_dict

def pretty_output(pos_list: list[dict[str,Any]]) -> str:
    output = "موقعیت های رانندگان:\n"
    for pos in sorted(pos_list, key=lambda pos: pos['position']):
        output += pos['position']+": "+pos['driver']['name_acronym']+str(pos['driver']['driver_number'])+"\n"
    return output
