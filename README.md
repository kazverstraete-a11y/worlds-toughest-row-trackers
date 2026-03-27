# World’s Toughest Row — Automated Daily Tracker & Context Engine for Team Madlantic

A Python project that fetches live leaderboard data from the World’s Toughest Row (Atlantic), stores daily snapshots, reconstructs race progress over time, and enriches each update with route-based marine weather context.

The result is an automated daily update that combines performance, ranking, progression, and sea-state conditions in a follower-friendly format.

## What it does
- Tracks:
  - 24h distance covered
  - total distance covered
  - progress percentage
  - remaining distance
  - solo and overall ranking
  - day-to-day rank changes
  - elapsed time since race start
- Reconstructs historical 24h performance over time
- Computes a rolling 5-day average for daily distance
- Interpolates current boat position from a KML race route
- Derives route bearing at the athlete’s current position
- Pulls live wind and marine conditions via Open-Meteo APIs
- Builds a sea-state difficulty score using wind, crosswind, swell, wave height, and wave period
- Generates:
  - a daily text update
  - a trend chart of 24h distance vs rolling average
- Saves daily snapshots (`data/`) and ready-to-share texts (`outputs/`)

## Tech highlights

- Python (json, pathlib, datetime, requests, pandas, matplotlib)
- Historical snapshot persistence for day-to-day race tracking
- Nested JSON parsing and metric extraction
- Geospatial route parsing from KML
- Position interpolation along a cumulative route distance
- Bearing calculation based on current route segment
- Marine weather enrichment through external APIs
- Custom sea-state scoring logic
- Automated text generation and chart export
- GitHub Actions scheduling + auto-commits

## Pipeline overview

1. Fetch live leaderboard JSON
2. Store daily snapshot locally
3. Extract Thomas’ current metrics
4. Rebuild historical daily 24h-distance series
5. Interpolate current position along the official route
6. Enrich with marine and wind conditions
7. Compute sea-state context score
8. Export daily text update and trend chart

## Why this project matters

This project goes beyond simple race tracking. It combines live competition data, route logic, historical trend reconstruction, and environmental context to produce updates that are both technically informative and readable for a broader audience.

It is a compact example of how raw external data can be transformed into structured, domain-aware communication.

## Example visual

Daily 24h covered distance over time, compared to a rolling 5-day average.  
This makes it easier to distinguish single strong days from broader performance trends during the crossing.

## Daily update output includes

- current solo and overall rank
- rank changes vs previous update
- 24h distance covered
- qualitative daily performance label
- 5-day performance comparison
- wind and wave context
- sea-state difficulty score
- total distance covered
- percentage of journey completed
- estimated rowing strokes
- elapsed time at sea
- remaining distance to Antigua

## Example output
```text
[🌊 World's Toughest Row - Dagelijkse update van 2025-12-22 
Thomas'statistieken sinds vorige update (2025-12-21-08:59) 

Solo klassement: 2e positie 
Algemeen klassement: 17e positie  

Afstand geroeid laatste 24u: 114.4 kilometer 
Totale afgelegde afstand: 1015.07 kilometer
.....omgerekend zijn dat 253767 roeislagen 

Thomas heeft al 21.15% van het hele avontuur voltooid 📊
Hij spendeert al 7 dagen 20.7 uur en 41 seconden op den 'Boiteau'


Voet aan wal op Antigua in.... 3784.93 kilometer]


