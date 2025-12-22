# worlds-toughest-row-trackers

Daily Python tracker for World’s Toughest Row (Team Madlantic)

Context:
  A Python script that automatically fetches live race data from the World’s Toughest Row Atlantic challenge and generates a daily, human-readable update for followers.

What the script does:
  Fetches daily leaderboard JSON data
  Extracts race metrics for a specific athlete
  Calculates:
    daily distance
    total distance
    race progress (%)
    elapsed time since race start
    day-to-day rank changes
Stores daily snapshots for comparison
Generates a ready-to-share text update

Technical highlights:
  Python
  JSON / nested data structures
  Datetime & timedelta
  File I/O for state persistence
  Cron automation
  Defensive coding (missing data handling)

Example output:

