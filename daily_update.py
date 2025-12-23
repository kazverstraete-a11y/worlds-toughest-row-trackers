import json
import urllib.request, urllib.parse, urllib.error
import ssl 
import pandas as pd
import numpy as np
import os
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

with open(filename, "w") as f: 
    json.dump(data, f, indent=2)

#open data from yesterday
yesterday = (date.today() - timedelta(days=1)).isoformat()
try: 
    filename = Path("data") / f"leaderboard_{yesterday}.json"
    with open(filename, "r") as f: 
        yesterday_data = json.load(f)
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

d24_today_km = round(thomas['d24'] * METERS_TO_KM, 2)
dmg_km = round(thomas['dmg'] * METERS_TO_KM, 2)
strokes = int((dmg_km * 1000) / 4)
distance_left = TOTAL_DISTANCE_KM - dmg_km
percent_done = round((dmg_km / TOTAL_DISTANCE_KM) * 100, 2)

#rank overall
today_overall_rank = thomas['rankR']
try:
    delta_overall = thomas['rankR'] - yesterday_thomas['rankR']
    if delta_overall > 0:
        delta_overall_str = f"(+{delta_overall} plaats(en))"
    elif diff_overal < 0:
        delta_overall_str = f"({delta_overall} plaats(en))"
    else:
        delta_overall_str = "(Zelfde plaats)"
except: 
    diff_str = ""

#rank solo
today_solo_rank = thomas_solo['rankR']
try:
    delta_rank_solo = thomas_solo['rankR'] - yesterday_thomas['rankR']
    if delta_rank_solo > 0:
        delta_solo_str = f"(+{delta_rank_solo} plaats(en) opgeschoven.)"
    elif diff_overal < 0:
        delta_solo_str = f"({delta_rank_solo} plaatsen(en) toegegeven.)"
    else:
        delta_solo_str = "(Zelfde plaats)"
except:
    delta_solo_str = ""

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

#deltas
d24_yesterday_km = round((yesterday_thomas['d24']*METERS_TO_KM), 2)
delta_d24 = d24_today_km - d24_yesterday_km
speed_24_today = d24_today_km / 24
speed_24_yesterday = d24_yesterday_km / 24
delta_speed = speed_24_today - speed_24_yesterday

#rolling averages
json_folder_path = Path('data')
files = list(json_folder_path.glob("*.json"))
recent_files = sorted(files, reverse=True)[1:6]

d24_list = list()
for file_path in recent_files: 
    with open(file_path, "r") as f:
        data = json.load(f)
    teams_o_data = data['tags'][0]['teams']
    thomas = next(team for team in teams_o_data if team['id'] == THOMAS_ID)
    d24_list.append(thomas['d24'] / 1000)

if len(d24_list) >= 2:
    avg_d24 = np.mean(d24_list)
    sd_d24 = round(np.std(d24_list, ddof=1), 2)
else: 
    avg_d24 = round(np.mean(d24_list), 2)
    sd_d24 = 0
    
#z-scores
score = "n.v.t."
z = None
if len(d24_list) >= 2 and sd_d24 > 0:
        z = (d24_today_km - avg_d24) / sd_d24
if z > 1.5:
        score = 5
elif z >0.5:
        score = 4
elif z >= -0.5:
        score = 3
elif z >= -1.5:
        score = 2
else:
        score = 1

EMOJI = {
    1: "🌊",
    2: "💨",
    3: "⚖️",
    4: "🌤️",
    5: "☀️"
}
emoji = EMOJI.get(score, "")
        
DAY_LABELS_CONDITIONS = {
    1: "Zware omstandigheden",
    2: "Tegenwerkende zee",
    3: "Neutrale omstandigheden",
    4: "Goede flow",
    5: "Perfecte dag op zee",
}

DAY_LABELS_PERFORMANCE = {
    1: "Hersteldag", 
    2: "Beheerde dag",
    3: "Stabiele dag",
    4: "Sterke dag",
    5: "Uitzonderlijke dag",
}

day_performance = DAY_LABELS_PERFORMANCE.get(score, "onvoldoende data")
day_conditions = DAY_LABELS_CONDITIONS.get(score, "onduidelijke omstandigheden")
    

#bericht
message = (
    f"\n\n"
    f"🌊 World's Toughest Row - Dagelijkse update van {now_strf} \n"
    f"Thomas'statistieken sinds vorige update ({yesterday}) \n\n"
    f"Solo klassement: {today_solo_rank}e positie {solo_str}\n"
    f"Algemeen klassement: {today_overall_rank}e positie {diff_str} \n\n"
    f"Vandaag lijkt op een {day_performance} {emoji} (Score {score}/5)\n"
    f"Thomas legde {d24_today_km.1f}km af in in 24u.\n"
    f"Mogelijk speelden hierbij ook {day_conditions} een rol.\n\n"
    f"Totale afgelegde afstand: {dmg_km} kilometer\n"
    f".....omgerekend zijn dat {strokes} roeislagen. \n\n"
    f"Thomas heeft al {percent_done}% van het hele avontuur voltooid 📊\n"
    f"Hij spendeert al {days} dagen {hours} uur en {seconds} seconden op den 'Boiteau'\n"
    f"Voet aan wal op Antigua in.... {distance_left} kilometer\n\n\n"
)

txtfile = Path("outputs") / f"update_{today}.txt"
with open(txtfile, "w") as handle: 
    handle.write(message)

print(message)
