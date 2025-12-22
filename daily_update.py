import json
import urllib.request, urllib.parse, urllib.error
import ssl 
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, datetime, timedelta

#ctx
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#url
url = urllib.request.urlopen('https://pro.yb.tl/JSON/wtrhtfrcm25/Leaderboard', context=ctx)
rr_url = url.read().decode()
data = json.loads(rr_url)

#save data
today = date.today().isoformat()
filename = Path("data") / f"leaderboard_{today}.json"

Path("data").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

with open(filename, "w") as handle: 
    json.dump(data, handle, indent=2)

#open data from yesterday
yesterday = (date.today() - timedelta(days=1)).isoformat()
try: 
    filename = Path("data") / f"leaderboard_{yesterday}.json"
    with open(filename, "r") as handle: 
        yesterday_data = json.load(handle)
except FileNotFoundError: 
    yesterday_data = None

THOMAS_ID = 40
#teams today
teams_o = data['tags'][0]['teams']
thomas = next(team for team in teams_o if team['id'] == THOMAS_ID)
teams_s = data['tags'][1]['teams']
thomas_solo = next(team for team in teams_s if team['id'] == THOMAS_ID)
#teams yesterday
try:
    yesterday_teams_o = yesterday_data['tags'][0]['teams']
    yesterday_thomas = next(team for team in yesterday_teams_o if team['id'] == THOMAS_ID)
    yesterday_teams_s = yesterday_data['tags'][1]['teams']
    yesterday_thomas_solo = next(team for team in yesterday_teams_s if team['id'] == THOMAS_ID)
except: 
    pass

#data
TOTAL_DISTANCE_KM = 4800
METERS_TO_KM = 1 / 1000

d24_km = round(thomas['d24'] * METERS_TO_KM, 2)
dmg_km = round(thomas['dmg'] * METERS_TO_KM, 2)
strokes = int((dmg_km * 1000) / 4)
distance_left = TOTAL_DISTANCE_KM - dmg_km
percent_done = round((dmg_km / TOTAL_DISTANCE_KM) * 100, 2)

#rank overall
today_overall_rank = thomas['rankR']
try:
    diff_overall = thomas['rankR'] - yesterday_thomas['rankR']
    if diff_overall > 0:
        diff_str = f"(+{diff_overall} plaats(en))"
    elif diff_overal < 0:
        diff_str = f"({diff_overall} plaats(en))"
    else:
        diff_str = "(Zelfde plaats)"
except: 
    diff_str = ""

#rank solo
today_solo_rank = thomas_solo['rankR']
try:
    diff_solo = thomas_solo['rankR'] - yesterday_thomas['rankR']
    if diff_solo > 0:
        solo_str = f"(+{diff_solo} plaats(en) opgeschoven.)"
    elif diff_overal < 0:
        solo_str = f"({diff_solo} plaatsen(en) toegegeven.)"
    else:
        solo_str = "(Zelfde plaats)"
except:
    solo_str = ""

#timeelapsed
START_TIME = datetime(
    year = 2025,
    month = 12,
    day = 14,
    hour = 12,
    minute = 18,
)
now = datetime.now()
now_strf = now.strftime("%Y-%m-%d")
date_today = date.today().isoformat()
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d-%H:%M")
elapsed = now - START_TIME
days = elapsed.days
hours = round(elapsed.seconds / 3600, 1)
seconds = int((elapsed.seconds % 3600) / 60)


#bericht
message = (
    f"\n\n"
    f"🌊 World's Toughest Row - Dagelijkse update van {now_strf} \n"
    f"Thomas'statistieken sinds vorige update ({yesterday}) \n\n"
    f"Solo klassement: {today_solo_rank}e positie {solo_str}\n"
    f"Algemeen klassement: {today_overall_rank}e positie {diff_str} \n\n"
    f"Afstand geroeid laatste 24u: {d24_km} kilometer \n"
    f"Totale afgelegde afstand: {dmg_km} kilometer\n"
    f".....omgerekend zijn dat {strokes} roeislagen \n\n"
    f"Thomas heeft al {percent_done}% van het hele avontuur voltooid 📊\n"
    f"Hij spendeert al {days} dagen {hours} uur en {seconds} seconden op den 'Boiteau'\n\n\n"
    f"Voet aan wal op Antigua in.... {distance_left} kilometer\n"
)

txtfile = Path("data/outputs") / f"update_{today}.txt"
with open(f"update_{date_today}.txt", "w") as handle: 
    handle.write(message)

print(message)
