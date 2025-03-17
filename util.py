import dateutil
import json
import requests
import logging
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
load_dotenv()

PROXIES = {"http":"http://127.0.0.1:2080",
           "https":"http://127.0.0.1:2080"}
#PROXIES = {}

# Base URLs for APIs
BASE_URL="https://api.openf1.org/v1/"  # OpenF1 API
TG_BASE_URL = f"https://api.telegram.org/bot{getenv("TG_TOKEN")}/"  # Telegram API


def session_driver_list(session_key: int) -> list[dict]:
    """
    Get list of all drivers participating in a race session

    Args:
        session_key (int): Unique session identifier

    Returns:
        list[dict]: List of dictionaries containing driver information
    """
    logging.debug(f"Fetching driver list for session {session_key}")
    resp = requests.get(BASE_URL+f"drivers?session_key={session_key}", proxies=PROXIES)
    return json.loads(resp.text)


def get_driver_position(driver_number:int, session_key:int):
    """
    Get the latest position of a specific driver in a race session

    Args:
        driver_number (int): Driver's number
        session_key (int): Unique session identifier

    Returns:
        int: Latest recorded position for the driver
    """
    logging.debug(f"Getting position for driver {driver_number} in session {session_key}")
    resp = requests.get(BASE_URL+f"position?session_key={session_key}&driver_number={driver_number}", proxies=PROXIES)
    return sorted(json.loads(resp.text), key=lambda pos: pos["date"])[-1]["position"]

def get_all_drivers_positions(session_key:int, driver_list:list[dict]):
    """
    Get all recorded positions for all drivers in a race session

    Args:
        session_key (int): Unique session identifier
        driver_list (list[dict]): List of drivers for adding supplementary information to positions

    Returns:
        list[dict]: List of all recorded positions with complete driver information
    """
    logging.debug(f"Fetching all positions for session {session_key}")
    resp = requests.get(BASE_URL+f"position?session_key={session_key}", proxies=PROXIES)
    pos_list = json.loads(resp.text)

    # Add driver information to each position and convert date to datetime object
    for pos in pos_list:
        pos["date"] = dateutil.parser.parse(pos["date"])
        driver = list(filter(lambda d: d['driver_number']==pos['driver_number'],driver_list))
        pos["driver"] = driver[0] 
    return pos_list


def get_last_drivers_position(session_key:int, driver_list: list[dict]):
    """
    Get the latest recorded position for each driver in a race session

    Args:
        session_key (int): Unique session identifier
        driver_list (list[dict]): List of drivers for adding supplementary information

    Returns:
        list[dict]: List of latest positions for each driver with complete information
    """
    logging.debug(f"Getting last positions for all drivers in session {session_key}")
    pos_list = get_all_drivers_positions(session_key, driver_list)
    pos_dict = {}
    
    # Find the latest position for each driver based on time
    for item in pos_list:
        position = item["position"]
        date = item["date"]
    
        # If we haven't seen this position yet, or if this record is newer
        if position not in pos_dict or date > pos_dict[position]["date"]:
            pos_dict[position] = item
    return list(pos_dict.values())


def get_last_session(year:int=datetime.now().year):
    """
    Get information about the latest race session in the specified year

    Args:
        year (int, optional): Target year. Defaults to current year.

    Returns:
        dict: Dictionary containing latest session information with dates converted to datetime
    """
    logging.info(f"Getting last session for year {year}")
    resp = requests.get(BASE_URL+f"sessions?year={year}", proxies=PROXIES)
    json_resp = json.loads(resp.text)
    
    # Sort sessions by start date and select the latest one
    ses_dict = sorted(json_resp, key=(lambda ses: dateutil.parser.parse(ses["date_start"])))[-1]
    ses_dict['date_start'] = dateutil.parser.parse(ses_dict['date_start'])
    ses_dict['date_end'] = dateutil.parser.parse(ses_dict['date_end'])
    return ses_dict

def get_meeting(meeting_key:int):
    """
    Get information about a race meeting with specified key

    Args:
        meeting_key (int): Unique meeting identifier

    Returns:
        dict: Dictionary containing meeting information
    """
    logging.debug(f"Fetching meeting info for meeting {meeting_key}")
    resp = requests.get(BASE_URL+f"meetings?meeting_key={meeting_key}", proxies=PROXIES)
    return json.loads(resp.text)[0]
