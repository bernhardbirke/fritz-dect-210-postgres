#!/usr/bin/env python3
# vim: expandtab sw=4 ts=4
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

LOGIN_SID_ROUTE = "/login_sid.lua?version=2"
AUTOSWITCH_ROUTE = "/webservices/homeautoswitch.lua"

class LoginState:
 def __init__(self, challenge: str, blocktime: int):
  self.challenge = challenge
  self.blocktime = blocktime
  self.is_pbkdf2 = challenge.startswith("2$")

def get_sid(box_url: str, username: str, password: str) -> str:
 """ Get a sid by solving the PBKDF2 (or MD5) challenge-response 
process. """
 try:
  state = get_login_state(box_url)
 except Exception as ex:
  raise Exception("failed to get challenge") from ex
 if state.is_pbkdf2:
  print("PBKDF2 supported")
  challenge_response = calculate_pbkdf2_response(state.challenge,
password)
 else:
  print("Falling back to MD5")
  challenge_response = calculate_md5_response(state.challenge,
password)
 if state.blocktime > 0:
  print(f"Waiting for {state.blocktime} seconds...")
  time.sleep(state.blocktime)
 try:
  sid = send_response(box_url, username, challenge_response)
 except Exception as ex:
  raise Exception("failed to login") from ex
 if sid == "0000000000000000":
  raise Exception("wrong username or password")
 return sid

def get_login_state(box_url: str) -> LoginState:
 """ Get login state from FRITZ!Box using login_sid.lua?version=2 """
 url = box_url + LOGIN_SID_ROUTE
 http_response = urllib.request.urlopen(url)
 xml = ET.fromstring(http_response.read())
 # print(f"xml: {xml}")
 challenge = xml.find("Challenge").text
 blocktime = int(xml.find("BlockTime").text)
 return LoginState(challenge, blocktime)


def calculate_pbkdf2_response(challenge: str, password: str) -> str:
 """ Calculate the response for a given challenge via PBKDF2 """
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

def calculate_md5_response(challenge: str, password: str) -> str:
 """ Calculate the response for a challenge using legacy MD5 """
 response = challenge + "-" + password
 # the legacy response needs utf_16_le encoding
 response = response.encode("utf_16_le")
 md5_sum = hashlib.md5()
 md5_sum.update(response)
 response = challenge + "-" + md5_sum.hexdigest()
 return response

def send_response(box_url: str, username: str, challenge_response: str) -> str:
 """ Send the response and return the parsed sid. raises an Exception on 
error """
 # Build response params
 post_data_dict = {"username": username, "response": challenge_response}
 post_data = urllib.parse.urlencode(post_data_dict).encode()
 headers = {"Content-Type": "application/x-www-form-urlencoded"}
 url = box_url + LOGIN_SID_ROUTE
 # Send response
 http_request = urllib.request.Request(url, post_data, headers)
 http_response = urllib.request.urlopen(http_request)
 # Parse SID from resulting XML.
 xml = ET.fromstring(http_response.read())
 return xml.find("SID").text

def retrieve_data(box_url:str, sid: str, switchcmd:str,ain: str = None, **kwargs) -> str | int:
    """
    get data from fritzbox using http requests.
    """
    parameter = {ain:ain, switchcmd:switchcmd,sid: sid}
    #add optional parameter
    parameter.update(kwargs)
    url = box_url + AUTOSWITCH_ROUTE
    response = requests.get(url, params=parameter)
    print(response.url)
    print(response.text)
    xml = ET.fromstring(response.content)
    
    # Extract challenge and blocktime
    #challenge = xml.find("Challenge").text
    #blocktime = int(xml.find("BlockTime").text)
    
  #  http://fritz.box/webservices/homeautoswitch.lua?ain=<ain>&switchcmd=<cmd>&sid=<sid>
  #  http://fritz.box/webservices/homeautoswitch.lua?switchcmd=getdevicelistinfos&sid=2fc2abc28cbadea1
  #  http://fritz.box/webservices/homeautoswitch.lua?ain=11657%200626533&switchcmd=gettemperature&sid=ae9e7c552595ca9e


def main():
 if len(sys.argv) < 4:
  print(
 f"Usage: {sys.argv[0]} http://fritz.box user pass"
 )
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
 url = os.getenv('URL_FRITZBOX') 
 username = os.getenv('USER_FRITZBOX')
 password = os.getenv('PASS_FRITZBOX')
 ain = os getenv('AIN_210_1')
 sid = get_sid(url, username, password)
 print(f"Successful login for user: {username}")
 print(f"sid: {sid}")
 switchcmd = getdevicelistinfos
 retrieve_data(url, sid, switchcmd)

if __name__ == "__main__":
 main_env()