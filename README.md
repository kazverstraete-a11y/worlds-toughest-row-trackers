# World’s Toughest Row — Daily Tracker for team Madlantic(Python)

A small Python pipeline that fetches live leaderboard JSON data for the World’s Toughest Row (Atlantic) and generates a daily follower-friendly update (WhatsApp/Instagram style).

## What it does
- Fetches leaderboard JSON snapshots
- Extracts Thomas’ metrics (by team id)
- Computes:
  - distance rowed last 24h (km)
  - total distance so far (km)
  - progress percentage
  - remaining distance (km)
  - elapsed time since race start (computed locally from start timestamp)
  - rank changes vs previous snapshot
- Saves daily snapshots (`data/`) and ready-to-share texts (`outputs/`)

## Tech highlights
- Python (requests/urllib, json)
- Nested JSON parsing (dict/list)
- datetime / timedelta
- File persistence for day-to-day diffs
- GitHub Actions scheduling + auto-commits

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


