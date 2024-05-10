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

def fetch_challenge(ip_fritzbox = None):
    """Fetch the challenge token from the FritzBox."""
    if not ip_fritzbox:
    	ip_fritzbox = os.getenv("IP_FRITZBOX")  
    response = requests.get(f"{ip_fritzbox}/login_sid.lua")
    root = ET.fromstring(response.content)
    return root.find('Challenge').text

if __name__ == "__main__":
    print(fetch_challenge())