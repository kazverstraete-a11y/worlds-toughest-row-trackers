# World’s Toughest Row — Automated Daily Tracker & Context Engine for Team Madlantic

A Python project that fetches live leaderboard data from the World’s Toughest Row (Atlantic), stores daily snapshots, reconstructs race progress over time, and enriches each update with route-based marine weather context.

The result is an automated daily update that combines performance, ranking, progression, and sea-state conditions in a follower-friendly format.

---

## What it does

- Fetches live leaderboard JSON data and stores daily snapshots locally
- Extracts Thomas’ metrics using team ID
- Tracks:
  - 24h distance covered
  - total distance covered
  - progress percentage
  - remaining distance
  - solo and overall ranking
  - day-to-day ranking changes
  - elapsed time since race start
- Reconstructs historical 24h performance over time
- Computes a rolling 5-day average for daily covered distance
- Interpolates current boat position along the official KML route
- Calculates route bearing at the current position
- Pulls live wind and marine weather data via Open-Meteo APIs
- Builds a sea-state difficulty score based on wind, crosswind, swell, wave height, and wave period
- Generates:
  - a daily text update
  - a performance trend chart
- Saves daily snapshots (`data/`) and ready-to-share texts (`outputs/`)

---

## Pipeline overview

1. Fetch live leaderboard JSON
2. Store daily snapshot in `data/`
3. Extract Thomas’ race metrics
4. Rebuild the historical daily 24h-distance series
5. Interpolate boat position along the official route
6. Enrich the current position with wind and marine conditions
7. Compute a sea-state context score
8. Export a daily text update and chart to `outputs/`

## Tech highlights

- Python
- `requests`, `json`, `pathlib`, `datetime`
- `pandas` for time series reconstruction
- `matplotlib` for trend visualization
- KML route parsing with `xml.etree.ElementTree`
- Haversine-based cumulative route distance
- Position interpolation and bearing calculation
- External weather enrichment through Open-Meteo APIs
- Automated text generation from live race + weather data
- GitHub Actions scheduling + auto-commits

---

## Why this project matters

This project goes beyond simple race tracking. It combines live competition data, route logic, historical trend reconstruction, and environmental context to produce updates that are both technically informative and readable for a broader audience.

It is a compact example of how raw external data can be transformed into structured, domain-aware communication.

---

## Example visual

Daily 24h distance over time with a rolling 5-day average.

The chart highlights momentum rather than single performances, making it easy to see when performance is building. During the race, this created a clear sense of progression that followers could track day by day.

![Alt text](https://github.com/kazverstraete-a11y/worlds-toughest-row-trackers/blob/main/outputs/d24_trend_2026-01-17.png)

---

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

---

## Example output
```text
🌊 World's Toughest Row – Daily update – 2026-01-18
Thomas' data and figures since the previous update (2026-01-17-19:28)

Solo rank: 2 position (Same place)
Overall rank: 17 position (Same place)

Today appears to be a Very strong day🌤️ (score 4/5).
(Score calculated by comparing with Thomas' 5-day average covered distance)

Thomas covered 157.2 km over the past 24 hours.
Wind & sea context:
    38.2 km/h with a clear tailwind.
    Waves around 3.2 m (period 8.1s).
Sea state today: Very challenging (75/100) — helpful context for today’s distance.
(score based up wave height, wind(head & cross), chop, swell°)

Thomas has now completed 82.59% of the entire journey 📊
Total distance covered: 4086.63 km. That is 1021657 rowing strokes.

He has been at sea for 35 days, 7.2 hours and 10 minutes aboard *Boiteau*.
Distance remaining to Antigua: 861.4 km

```

---

## Note

The race started on 2025-12-14, but this tracker was built after the event had already started.  
As a result, the historical trend begins from the first stored local snapshot rather than from race day 1.

