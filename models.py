import logging
import requests
import json
import util
from util import TG_BASE_URL as BASE_URL
from datetime import datetime, timedelta, timezone


class TelegramUpdateBot:
    """
    A class for managing a Telegram bot that updates Formula 1 race status.
    This class is responsible for sending and updating messages in a Telegram chat
    and maintains information about drivers and their positions during the race.

    Attributes:
        chat_id (str): Telegram chat ID where messages will be sent
        current_message_id (int): ID of the last sent message
        last_update_time (datetime): Time of the last data update
        current_session (dict): Current race session information
        current_meeting (dict): Current race meeting information
        driver_list (list): List of participating drivers
        position_list (list): List of current driver positions
    """

    def __init__(self, chat_id: str):
        """
        Initialize the bot with a specified chat ID

        Args:
            chat_id (str): Telegram chat ID for sending messages
        """
        logging.info(f"Initializing TelegramUpdateBot for chat {chat_id}")
        self.chat_id=chat_id
        self.current_message_id=6
        self.last_new_message_time=0
        self.last_update_time=datetime(1,1,1)
        self.next_update_time=datetime(1,1,1)
        self.current_session={}
        self.current_meeting={}
        self.driver_list=[]
        self.position_list=[]
        self.overtakes = []

    def update_message(self, text):
        """
        Update the text of the current message in Telegram chat

        Args:
            text (str): New text for updating the message

        Returns:
            dict: Telegram API response to the edit request
        """
        logging.debug("Updating message with id: "+str(self.current_message_id))
        resp = requests.get(BASE_URL+f"editMessageText?chat_id={self.chat_id}&message_id={self.current_message_id}&text={text}", proxies=util.PROXIES)
        return json.loads(resp.text)

    def send_new_message(self):
        """
        Send a new message in Telegram chat with current race information

        Returns:
            dict: Telegram API response to the send request
        """
        logging.debug("Sending a new message")
        text = self.pretty_data()
        resp = requests.get(BASE_URL+f"sendMessage?chat_id={self.chat_id}&text={text}", proxies=util.PROXIES)
        json_resp = json.loads(resp.text)
        self.current_message_id = json_resp['result']['message_id']
        return json_resp['result']

    def tg_logout(self):
        """
        Logout from Telegram API

        Returns:
            dict: Telegram API response to the logout request
        """
        logging.info("Logging out from Telegram")
        resp = requests.get(BASE_URL+'logout', proxies=util.PROXIES)
        return json.loads(resp.text)

    def fetch_session_and_drivers(self):
        """
        Fetch current race session information and driver list.
        This method updates current_session, current_meeting, and driver_list.
        """
        logging.info("Fetching current session and driver information")
        self.current_session = util.get_last_session()
        self.current_meeting = util.get_meeting(self.current_session['meeting_key'])
        self.driver_list = util.session_driver_list(self.current_session['session_key'])
        self.last_update_time = datetime.now()
        logging.debug(f"Current session: {self.current_session['official_name']}")

    def pretty_data(self) -> str:
        output = "🕓آخرین بروزرسانی: "+self.last_update_time.astimezone(timezone(timedelta(hours=3,minutes=30))).strftime("%H:%M:%S")+"\n"
        output += self.current_meeting['meeting_official_name'] + "\n"
        output += "🏎️رقابت: "+self.current_session['session_name']+"\n"
        output += "📈موقعیت های رانندگان:\n"
        for pos in sorted(self.position_list, key=lambda pos: pos['position']):
            if pos['position'] == 1 and datetime.now(timezone.utc)>pos['date']:
                pos_str = '🏆 '  # Race winner
            elif pos['position'] == 1:
               pos_str = '🥇 '  # First place
            elif pos['position'] == 2:
               pos_str = '🥈 '  # Second place
            elif pos['position'] == 3:
               pos_str = '🥉 '  # Third place
            else:
                pos_str = str(pos['position'])+'. '
            output += pos_str+pos['driver']['first_name']+" "+pos['driver']['last_name']+" ("+str(pos['driver']['driver_number'])+")\n"
        if len(self.overtakes) > 0:
            output += "\nسبقت ها:\n"
            for ovrt in self.overtakes:
                output += ovrt['date'].strftime('%H:%M:%S')+" رتبه "+ovrt['position']+": "+util.get_driver_id(ovrt['overtaking_driver'])+" از "+util.get_driver_id(ovrt['overtaken_driver'])
            
        return output
    
    
    def fetch_new_positions(self):
        """
        Fetch latest driver positions in the current race and detect any overtakes.
        This method updates position_list with the latest position information and
        tracks any overtakes that occurred.
        """
        logging.debug("Fetching new driver positions")
        new_positions = util.get_last_drivers_position(self.current_session['session_key'], self.driver_list)
        self.last_update_time = datetime.now()
        
        # Detect overtakes before updating position list
        if hasattr(self, 'position_list') and self.position_list:
            # Sort both lists by position for comparison
            old_positions = sorted(self.position_list, key=lambda x: x['position'])
            new_positions_sorted = sorted(new_positions, key=lambda x: x['position'])
            
            # Compare driver numbers at each position to detect changes
            for old_pos, new_pos in zip(old_positions, new_positions_sorted):
                if old_pos['driver_number'] != new_pos['driver_number']:
                    # Find the old position of the driver who is now in this position
                    old_pos_of_overtaker = next(
                        (p for p in old_positions if p['driver_number'] == new_pos['driver_number']),
                        None
                    )
                    
                    if old_pos_of_overtaker and old_pos_of_overtaker['position'] > old_pos['position']:
                        self.overtakes.append({
                            'date': new_pos['date'],
                            'position': new_pos['position'],
                            'overtaking_driver': new_pos['driver'],
                            'overtaken_driver': old_pos['driver']
                        })
        
        self.position_list = new_positions

