#!/usr/bin/env python3
"""
FRITZ!OS WebGUI Login
Get a sid (session ID) via PBKDF2 based challenge response algorithm.
Fallback to MD5 if FRITZ!OS has no PBKDF2 support.
AVM 2020-09-25
"""
import sys
import hashlib
import time
import requests
import urllib.request

import urllib.parse
import xml.etree.ElementTree as ET




class LoginState:
    def __init__(self, challenge: str, blocktime: int):
        self.challenge = challenge
        self.blocktime = blocktime
        self.is_pbkdf2 = challenge.startswith("2$")

class DectToPostgres():

  def __init__(self,
  config: Configuration,
  client: PostgresTasks, 
  box_url: str,
  ):
   self.config = config
   self.client = client
   self.LOGIN_SID_ROUTE = "/login_sid.lua?version=2"
   self.AUTOSWITCH_ROUTE = "/webservices/homeautoswitch.lua"
   self.print_console = True
   self.to_postgresql = False
   self.BACKOFF_INTERVAL: int = 30 #pause 30 seconds between data requests
  

  def get_sid(self, box_url: str, username: str, password: str) -> str:
    """Get a sid by solving the PBKDF2 (or MD5) challenge-response
    process."""
    try:
        state = self.get_login_state(box_url)
    except Exception as ex:
        raise Exception("failed to get challenge") from ex
    if state.is_pbkdf2:
        print("PBKDF2 supported")
        challenge_response = self.calculate_pbkdf2_response(state.challenge, password)
    else:
        print("Falling back to MD5")
        challenge_response = self.calculate_md5_response(state.challenge, password)
    if state.blocktime > 0:
        print(f"Waiting for {state.blocktime} seconds...")
        time.sleep(state.blocktime)
    try:
        sid = self.send_response(box_url, username, challenge_response)
    except Exception as ex:
        raise Exception("failed to login") from ex
    if sid == "0000000000000000":
        raise Exception("wrong username or password")
    return sid

  def validate_sid(self, box_url: str, sid: str) -> True | False:
  """ Tests if sid is valid. Returns True when valid, otherwise False"""
     parameter = {"sid": sid}
     url = box_url + self.LOGIN_SID_ROUTE 
     response = requests.get(url, params=parameter)
     return response
 
  

  def get_login_state(self, box_url: str) -> LoginState:
    """Get login state from FRITZ!Box using login_sid.lua?version=2"""
    url = box_url + self.LOGIN_SID_ROUTE
    http_response = urllib.request.urlopen(url)
    xml = ET.fromstring(http_response.read())
    # print(f"xml: {xml}")
    challenge = xml.find("Challenge").text
    blocktime = int(xml.find("BlockTime").text)
    return LoginState(challenge, blocktime)


  def calculate_pbkdf2_response(self, challenge: str, password: str) -> str:
    """Calculate the response for a given challenge via PBKDF2"""
    challenge_parts = challenge.split("$")
    # Extract all necessary values encoded into the challenge
    iter1 = int(challenge_parts[1])
    salt1 = bytes.fromhex(challenge_parts[2])
    iter2 = int(challenge_parts[3])
    salt2 = bytes.fromhex(challenge_parts[4])
    # Hash twice, once with static salt...
    hash1 = hashlib.pbkdf2_hmac("sha256", password.encode(), salt1, iter1)
    # Once with dynamic salt.
    hash2 = hashlib.pbkdf2_hmac("sha256", hash1, salt2, iter2)
    return f"{challenge_parts[4]}${hash2.hex()}"


  def calculate_md5_response(self, challenge: str, password: str) -> str:
    """Calculate the response for a challenge using legacy MD5"""
    response = challenge + "-" + password
    # the legacy response needs utf_16_le encoding
    response = response.encode("utf_16_le")
    md5_sum = hashlib.md5()
    md5_sum.update(response)
    response = challenge + "-" + md5_sum.hexdigest()
    return response


  def send_response(self, box_url: str, username: str, challenge_response: str) -> str:
    """Send the response and return the parsed sid. raises an Exception on
    error"""
    # Build response params
    post_data_dict = {"username": username, "response": challenge_response}
    post_data = urllib.parse.urlencode(post_data_dict).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = box_url + self.LOGIN_SID_ROUTE
    # Send response
    http_request = urllib.request.Request(url, post_data, headers)
    http_response = urllib.request.urlopen(http_request)
    # Parse SID from resulting XML.
    xml = ET.fromstring(http_response.read())
    return xml.find("SID").text


  def retrieve_data(
    self, box_url: str, sid: str, switchcmd: str, ain: str = None, **kwargs
) -> str | int:
    """
    get data from fritzbox using http requests.
    """
    parameter = {"ain": ain, "switchcmd": switchcmd, "sid": sid}
    # add optional parameter
    parameter.update(kwargs)
    url = box_url + self.AUTOSWITCH_ROUTE
    response = requests.get(url, params=parameter)
    # print(response.url)
    return response.text


  def run(self) -> None:
    try:
        logging.info(f"Application started")
        dect210_config = self.config.dect210_config()
        url = dect210_config["url"]
        username = dect210_config["user"] 
        password = dect210_config["password"]
        ain_210 = dect210_config["ain"]
      while True:
        try:
           if not self.validate_sid(url, self.sid):
              self.sid = get_sid(url, username, password)
              logging.info(f"Successful login for user: {username}")
              logging.info(f"sid: {sid}")
           
           #retrieve data from switch
           #switchcmd = "getdevicelistinfos"
           switchcmd = "getswitchpower" # Leistung in mW, "inval" wenn unbekannt
           switch_power = int(retrieve_data(url, sid, switchcmd, ain = ain_210)) / 1000 #in W
           
           switchcmd = "getswitchenergy" # Energie in Wh seit Erstinbetriebnahme, "inval" wenn unbekannt
           switch_energy = int(retrieve_data(url, sid, switchcmd, ain = ain_210))
           
           switchcmd = "gettemperature" # Temperatur-Wert in 0,1 °C, 
           switch_temperature = int(retrieve_data(url, sid, switchcmd, ain = ain_210)) /10 #in °C
           
           
           if print_console:
               print(f"power: {switch_power} W")
               print(f"energy: {switch_energy} Wh")
               print(f"temperature: {switch_temperature} °C")
           
           
           #save data to postgresql database
           if to_postgresql:
               self.data_id = self.client.insert_dect_210(power,energy,temperature)
               logging.info(f"Data written. Data id: {self.data_id}")
               sleep(self.BACKOFF_INTERVAL)

        except ConnectionError:
           logging.error("No Connection available", exc_info=True)
           sleep(10)
           logging.info("Waited 10 seconds for connection")
        except Exception as e:
           logging.error("Exception: {}".format(e), exc_info=True)
           sys.exit(1)
    
    except KeyboardInterrupt:
    logging.info("Stopping program.")


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} http://fritz.box user pass")
        exit(1)
    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    sid = get_sid(url, username, password)
    print(f"Successful login for user: {username}")
    print(f"sid: {sid}")


def main_env():
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    # Access environment variables using os.
    url = os.getenv("URL_FRITZBOX")
    username = os.getenv("USER_FRITZBOX")
    password = os.getenv("PASS_FRITZBOX")
    ain_210 = os.getenv("AIN_210_1")
    sid = get_sid(url, username, password)
    print(f"Successful login for user: {username}")
    print(f"sid: {sid}")
    switchcmd = "getdevicelistinfos"
    switchcmd = "getswitchpower"  # Leistung in mW, "inval" wenn unbekannt
    switchcmd = "getswitchenergy"  # Energie in Wh seit Erstinbetriebnahme, "inval" wenn unbekannt
    switchcmd = "gettemperature"  # Temperatur-Wert in 0,1 °C, negative und positive Werte möglichBsp. „200“ bedeutet 20°C
    retrieve_data(url, sid, switchcmd, ain=ain_210)


if __name__ == "__main__":
    main_env()