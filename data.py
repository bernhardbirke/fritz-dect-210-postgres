import os
import requests
import hashlib
import sys
import xml.etree.ElementTree as ET

# load environment variables such as the directories to raw data files
from dotenv import load_dotenv

load_dotenv()

# Constants
#IP_FRITZBOX = os.getenv("IP_FRITZBOX") 
#USER = os.getenv("USER")
#PASSWORD = os.getenv("PASSWORD")


#runfile with python fritzbox_reader.py <device_name> <value_type> 

def fetch_challenge(ip_fritzbox = None) -> str:
    """Fetch the challenge token from the FritzBox. and return it. (ie 299bad94)"""
    if not ip_fritzbox:
    	ip_fritzbox = os.getenv("IP_FRITZBOX")  
    response = requests.get(f"{ip_fritzbox}/login_sid.lua")
    root = ET.fromstring(response.content)
    return root.find('Challenge').text

def perform_login(challenge, ip_fritzbox = None, username = None, password = None) -> str:
    """Perform login using the challenge, username and password, return the session ID."""
    if not ip_fritzbox:
    	ip_fritzbox = os.getenv("IP_FRITZBOX")
    if not username:
    	username = os.getenv("USER")
    if not password:
    	password = os.getenv("PASS")
    
    md5 = hashlib.md5((challenge + '-' + password).encode('utf-16le')).hexdigest()
    response = challenge + '-' + md5
    login_response = requests.post(f"{ip_fritzbox}/login_sid.lua", data={'response': response, 'username': username})
    root = ET.fromstring(login_response.content)
    return root.find('SID').text



if __name__ == "__main__":
    challenge = fetch_challenge()
    sid = perform_login(challenge)
    print(sid)