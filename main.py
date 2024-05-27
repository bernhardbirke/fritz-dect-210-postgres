import os
from dotenv import load_dotenv
from data import get_sid, retrieve_data

# Load environment variables from .env file
load_dotenv()


print_console = True
to_postgresql = False

# Access environment variables using os. 
url = os.getenv('URL_FRITZBOX') 
username = os.getenv('USER_FRITZBOX')
password = os.getenv('PASS_FRITZBOX')
ain_210 = os.getenv('AIN_210_1')


sid = get_sid(url, username, password)
print(f"Successful login for user: {username}")
print(f"sid: {sid}")

#retrieve data from switch
#switchcmd = "getdevicelistinfos"
switchcmd = "getswitchpower" # Leistung in mW, "inval" wenn unbekannt
switch_power = int(retrieve_data(url, sid, switchcmd, ain = ain_210)) / 1000 #in W

switchcmd = "getswitchenergy" # Energie in Wh seit Erstinbetriebnahme, "inval" wenn unbekannt
switch_energy = int(retrieve_data(url, sid, switchcmd, ain = ain_210))

switchcmd = "gettemperature" # Temperatur-Wert in 0,1 °C, negative und positive WertemöglichBsp. „200“ bedeutet 20°C
switch_temperature = int(retrieve_data(url, sid, switchcmd, ain = ain_210)) /10 #in °C


if print_console:
    print(f"power: {switch_power} W")
    print(f"energy: {switch_energy} Wh")
    print(f"temperature: {switch_temperature} W")


#save data to postgresql database
if to_postgresql:
    pass