import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import math


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
    if i is None or i is == len(route_df)-1:
        raise ValueError("Kon geen geldig segment vinden (dmg_km buiten route?).")
    return i, dmg_km

#interpolate position
def interpolate_position(route_df, dmg_km):
    
    """
    Interpoleert positie op basis van dmg_km (totale afstand sinds start).
    Returns: (lat, lon, i) waarbij i het segment is.
    """"
    
    i, dmg_km = find_segment(route_df, dmg_km)
    km0 = route_df.loc[i, 'cum_km']
    km1 = route_df.loc[i + 1, 'cum_km']
    
    t = (dmg_km - km0) / (km1 - km0) #fractie binnen het segment 
    
    lat0, lon0 = route_df.loc[i, ['lat', 'lon']]
    lat1, lon1 = route_df.loc[i, ['lat', 'lon']]
    
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

