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
[plak hier een voorbeeld van je update]


