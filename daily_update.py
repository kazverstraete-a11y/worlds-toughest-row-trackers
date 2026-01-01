import json
import urllib.request, urllib.parse, urllib.error
import ssl 
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
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
        delta_overall_str = f"(-{delta_overall} place(s))"
    elif delta_overall < 0:
        delta_overall_str = f"(+{abs(delta_overall)} place(s))"
    else:
        delta_overall_str = "(Same place)"
except: 
    delta_overall_str = ""

#rank solo
today_solo_rank = thomas_solo['rankR']
try:
    delta_rank_solo = thomas_solo['rankR'] - yesterday_thomas_solo['rankR']
    if delta_rank_solo < 0:
        delta_solo_str = f"(+{delta_rank_solo} place(s))"
    elif delta_rank_solo > 0:
        delta_solo_str = f"({delta_rank_solo} place(s))"
    else:
        delta_solo_str = "(Same place)"
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
recent_files = sorted(files, reverse=True)

rows = list()

for file_path in recent_files: 
    with open(file_path, "r") as f:
        data = json.load(f)
    teams_o_data = data['tags'][0]['teams']
    thomas = next(team for team in teams_o_data if team['id'] == THOMAS_ID)
    
    d24_km = thomas['d24'] / 1000

    file_date_str = file_path.stem.replace("leaderboard_", "")
    file_date = pd.to_datetime(file_date_str)
    rows.append((file_date, d24_km))

df = (
    pd.DataFrame(rows, columns=["date", "d24_km"])
    .sort_values("date")
    .reset_index(drop=True)
)

dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
d24_list = df["d24_km"].tolist()

df["d24_ma5"] = df["d24_km"].rolling(window=5, min_periods=1).mean()
last5_avg = float(df["d24_km"].tail(5).mean())
ma5_today = float(df["d24_ma5"].iloc[-1])
d24_today_km = float(df["d24_km"].iloc[-1])


if len(d24_list) >= 2:
    avg_d24 = np.mean(d24_list)
    sd_d24 = round(np.std(d24_list, ddof=1), 2)
else: 
    avg_d24 = round(np.mean(d24_list), 2)
    sd_d24 = 0
    
#z-scores
score = "n.v.t."
z = None

baseline = ma5_today

if len(d24_list) >= 2 and sd_d24 > 0:
    z = (d24_today_km - baseline) / sd_d24
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
    1: "Challenging conditions",
    2: "Headwinds and adverse seas",
    3: "Neutral conditions",
    4: "Favourable flow",
    5: "Perfect day at sea",
}

DAY_LABELS_PERFORMANCE = {
    1: "Controlled day",
    2: "Steady day",
    3: "Strong day",
    4: "Very strong day",
    5: "Exceptional day",
}

#helper
def fmt_km(x):
    return f"{x:.1f}" if isinstance (x, (int, float)) else "n.v.t."

if score == "n.v.t.":
    day_sentence = (
           "Today appears to be a strong day at sea.\n"
            f"Thomas covered {fmt_km(d24_today_km)} km over the past 24 hours.\n"
            "More data is needed before this effort can be objectively classified."
    )
else:
    day_performance = DAY_LABELS_PERFORMANCE.get(score, "insufficient data")
    day_conditions = DAY_LABELS_CONDITIONS.get(score, "unclear conditions")
    day_sentence = (
        f"Thomas covered {fmt_km(d24_today_km)} km over the past 24 hours.\n"
        f"Today appears to be a {day_performance}{emoji} (score {score}/5).\n"
        f"Sea conditions (i.e. {day_conditions} ) may have influenced this effort.\n"
        f"(Score calculated by comparing with Thomas' 5-day average covered distance)"
    )

#bericht
message = (
    f"\n"
    f"🌊 World's Toughest Row – Daily update – {now_strf}\n"
    f"Thomas' data and figures since the previous update ({yesterday})\n\n"
    f"Solo rank: {today_solo_rank} position {delta_solo_str}\n"
    f"Overall rank: {today_overall_rank} position {delta_overall_str}\n\n"
    f"{day_sentence}\n\n"
    f"Thomas has now completed {percent_done}% of the entire journey 📊\n"
    f"Total distance covered: {dmg_km} km\n"
    f"...equivalent to {strokes} rowing strokes.\n\n"
    f"He has been at sea for {days} days, {hours} hours and {seconds} seconds aboard *Boiteau*.\n"
    f"Distance remaining to Antigua: {fmt_km(distance_left)} km\n\n"
)

txtfile = Path("outputs") / f"update_{today}.txt"
with open(txtfile, "w") as handle: 
    handle.write(message)

print(message)

#trendvisual afgelegde kms per 24u
plt.figure(figsize=(8, 4))
plt.plot(df["date"], df["24_km"], marker="o", label="24h distance")
plt.axhline(df["date"], df["d24_ma5"], linestyle="--", color="grey", alpha=0.6, label="5-day average")
plt.axhline(last5_avg, linestyle=":", alpha=0.6, label="avg last 5 days")

plt.title("Distance last 24h - World's Toughest Row")
plt.ylabel("Kilometer")
plt.xlabel("Date")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(f"outputs/d24_trend_{date_today}.png")
plt.close()


