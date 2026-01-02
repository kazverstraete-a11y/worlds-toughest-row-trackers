import json
import urllib.request, urllib.parse, urllib.error
import ssl 
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import math
import requests
from pathlib import Path
from datetime import date, datetime, timedelta, timezone


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

#meteodata
def read_kml_coordinates(kml_path):
    tree = ET.parse(kml_path)
    root = tree.getroot() #root is entrypoint for the entire tree
    
    coords_element = root.find(".//{*}coordinates")
    if coords_element is None or not coords_element.text:
        raise ValueError("Geen coordinates gevonden in het KML-bestand")
        
    raw = coords_element.text.strip()
    
    points = list()
    for chunk in raw.replace("\n", " ").split():
        parts = chunk.split(",")
        if len(parts) < 2:
            continue
        lon = float(parts[0])
        lat = float(parts[1])
        points.append((lat, lon))
    
    if len(points) < 2:
        raise ValueError(f"Te weinig punten gevonden: {len(points)}")
        
    return points

#variables
coordinates = read_kml_coordinates('route.kml')
route_df = pd.DataFrame(coordinates, columns=['lat', 'lon'])

#cumulatieve afstand langsheen de route, haversine formule = afstand tussen twee punten op een bol(sferische afstand)
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2 * R * math.asin(math.sqrt(a))

lat_prev = route_df['lat'].shift(1)
lon_prev = route_df['lon'].shift(1)

route_df['seg_km'] = [
    np.nan if pd.isna(a) else haversine_km(a, b, c, d)
    for a, b, c, d in zip(lat_prev, lon_prev, route_df['lat'], route_df['lon'])
]

route_df['seg_km'] = route_df['seg_km'].fillna(0.0)
route_df['cum_km'] = route_df['seg_km'].cumsum()

#findsegment
def find_segment(route_df, dmg_km):
    """
    Zoekt i zodat cum_km[i] <= dmg_km < cum_km[i + 1]
    Geeft index i terug.
    """
    #safety voor moest dmg_km voorbij het einde zijn
    max_km = route_df['cum_km'].iloc[-1]
    if dmg_km >= max_km:
        dmg_km = max_km -1e-9
    if dmg_km < 0:
        raise ValueError("Dmg_km is negatief")
        
    i = route_df[route_df['cum_km'] <= dmg_km].index.max()
    if i is None or i == len(route_df)-1:
        raise ValueError("Kon geen geldig segment vinden (dmg_km buiten route?).")
    return i, dmg_km

#interpolate position
def interpolate_position(route_df, dmg_km):
    
    """
    Interpoleert positie op basis van dmg_km (totale afstand sinds start).
    Returns: (lat, lon, i) waarbij i het segment is.
    """
    
    i, dmg_km = find_segment(route_df, dmg_km)
    km0 = route_df.loc[i, 'cum_km']
    km1 = route_df.loc[i + 1, 'cum_km']
    
    t = (dmg_km - km0) / (km1 - km0) #fractie binnen het segment 
    
    lat0, lon0 = route_df.loc[i, ['lat', 'lon']]
    lat1, lon1 = route_df.loc[i + 1, ['lat', 'lon']]
    
    lat = lat0 + t *(lat1 - lat0)
    lon = lon0 + t * (lon1 - lon0)
    
    return lat, lon, i

#bearing = clockwise directen
def bearing_deg(lat1, lon1, lat2, lon2):
    """
    Bearing in graden (0-360): richting van punt1 naar punt2.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    
    y = math.sin(dlambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2)
        - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda))

    brng = math.degrees(math.atan2(y, x))
    return (brng + 360) % 360

#in een call alles bepalen
def position_and_bearing_from_dmg(route_df, dmg_km):
    """
    Convenience: in één call positie + bearing.
    Returns: (lat, lon, bearing, segment_index)
    """
    lat, lon, i = interpolate_position(route_df, dmg_km)

    brng = bearing_deg(
        route_df.loc[i, 'lat'], route_df.loc[i, 'lon'],
        route_df.loc[i + 1, 'lat'], route_df.loc[i + 1, 'lon']
    )
    return lat, lon, brng, i

lat, lon, brng, seg_i = position_and_bearing_from_dmg(route_df, dmg_km)

#koppelen aan marine weather api 
def get_marine_hourly(lat: float, lon: float, timezone: str = "UTC"):
    """
    Haalt uurlijkse wind + golfdata op via Open-Meteo Marine API.
    Returns: dict (JSON response)
    """
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "wind_speed_10m",
            "wind_direction_10m",
            "wave_height",
            "wave_direction",
            "wave_period",
        ]),
        "timezone": timezone,
    }
    
    r = requests.get(url, params = params, timeout=30)
    r.raise_for_status
    return r.json()

def pick_nearest_hour(marine_json: dict, target_dt: datetime):
    """
    marine_json: output van get_marine_hourly
    target_dt: datetime in dezelfde timezone als je request (bv. UTC)
    Returns: dict met de gekozen waarden
    """
    
    hourly = marine_json["hourly"]
    times = hourly["time"]
    
    target = target_dt.timestamp()
    best_i = None
    best_diff = None
    for i, t in enumerate(times):
        dt = datetime.fromisoformat(t)
        diff = abs(dt.timestamp() - target)
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_i = i
    return {
        "time": times[best_i],
        "wind_speed_10m": hourly["wind_speed_10m"][best_i],
        "wind_direction_10m": hourly["wind_direction_10m"][best_i],
        "wave_height": hourly["wave_height"][best_i],
        "wave_direction": hourly["wave_direction"][best_i],
        "wave_period": hourly["wave_period"][best_i],
    }
    
marine = get_marine_hourly(lat, lon, timezone="UTC")
marine_now = pick_nearest_hour(marine, now)

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

print("route_len_km:", route_df["cum_km"].iloc[-1])
print("dmg_km:", dmg_km)
print("progress %:", dmg_km / route_df["cum_km"].iloc[-1] * 100)
print("lat/lon:", lat, lon)
print("bearing:", brng)
print("Wind:", marine_now["wind_speed_10m"], "m/s @", marine_now["wind_direction_10m"], "°")
print("Waves:", marine_now["wave_height"], "m,", marine_now["wave_period"], "s @", marine_now["wave_direction"], "°")

print(marine_json["hourly"].keys())

#trendvisual afgelegde kms per 24u
plt.figure(figsize=(8, 4))
plt.plot(df["date"], df["d24_km"], marker="o", label="24h distance")
plt.plot(df["date"], df["d24_ma5"], linestyle="--", color="grey", alpha=0.8, label="5-day average")
plt.axhline(last5_avg, linestyle=":", alpha=0.6, label="avg last 5 days")

plt.fill_between(
    df["date"],
    df["d24_ma5"] - 5,
    df["d24_ma5"] + 5,
    alpha=0.1,
)

plt.title("Distance last 24h - World's Toughest Row")
plt.ylabel("Kilometer")
plt.xlabel("Date")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(f"outputs/d24_trend_{date_today}.png")
plt.close()



