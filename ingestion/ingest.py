"""
ingest.py
---------
Pulls current weather + air-quality data for a set of regions from the
Open-Meteo public API and loads it into Snowflake as raw records.

This is the "E" and "L" of ELT: Extract from the API, Load into Snowflake.
The "T" (transform) happens later in dbt.
"""

import os
import datetime
import requests
import snowflake.connector
from dotenv import load_dotenv

# Load secrets (Snowflake credentials) from a local .env file.
# These are NEVER hard-coded and NEVER pushed to GitHub.
load_dotenv()

# ---------------------------------------------------------------------------
# 1. CONFIG: the regions we monitor.
#    Each region is just a name + its latitude/longitude.
#    Add or remove freely — the pipeline loops over whatever is here.
# ---------------------------------------------------------------------------
REGIONS = [
    {"name": "Los Angeles", "lat": 34.05, "lon": -118.24},
    {"name": "San Francisco", "lat": 37.77, "lon": -122.42},
    {"name": "Sacramento", "lat": 38.58, "lon": -121.49},
    {"name": "Denver", "lat": 39.74, "lon": -104.99},
    {"name": "Phoenix", "lat": 33.45, "lon": -112.07},
    {"name": "Portland", "lat": 45.52, "lon": -122.68},
]

# API base URLs (Open-Meteo — free, no API key required)
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


# ---------------------------------------------------------------------------
# 2. EXTRACT: fetch weather + air quality for one region.
# ---------------------------------------------------------------------------
def fetch_region(region):
    """Call both APIs for a single region and return a combined record."""

    # --- Weather call: temperature, humidity, wind (the fire-risk conditions)
    weather_resp = requests.get(
        WEATHER_URL,
        params={
            "latitude": region["lat"],
            "longitude": region["lon"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        },
        timeout=30,
    )
    weather_resp.raise_for_status()          # stop loudly if the API errors
    weather = weather_resp.json()["current"]

    # --- Air-quality call: PM2.5 and PM10 (the smoke / pollution effect)
    air_resp = requests.get(
        AIR_URL,
        params={
            "latitude": region["lat"],
            "longitude": region["lon"],
            "current": "pm2_5,pm10",
        },
        timeout=30,
    )
    air_resp.raise_for_status()
    air = air_resp.json()["current"]

    # --- Combine both into one tidy record
    return {
        "region": region["name"],
        "latitude": region["lat"],
        "longitude": region["lon"],
        "collected_at": datetime.datetime.utcnow(),
        "temperature_c": weather.get("temperature_2m"),
        "humidity_pct": weather.get("relative_humidity_2m"),
        "wind_speed_kmh": weather.get("wind_speed_10m"),
        "pm2_5": air.get("pm2_5"),
        "pm10": air.get("pm10"),
    }


# ---------------------------------------------------------------------------
# 3. LOAD: write the records into Snowflake.
# ---------------------------------------------------------------------------
def load_to_snowflake(records):
    """Connect to Snowflake and insert all records into the raw table."""

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="RAW",
    )
    cur = conn.cursor()

    # Make sure the raw table exists (safe to run every time).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS RAW.AIR_WEATHER_RAW (
            region          STRING,
            latitude        FLOAT,
            longitude       FLOAT,
            collected_at    TIMESTAMP_NTZ,
            temperature_c   FLOAT,
            humidity_pct    FLOAT,
            wind_speed_kmh  FLOAT,
            pm2_5           FLOAT,
            pm10            FLOAT
        )
    """)

    # Insert every record we collected this run.
    insert_sql = """
        INSERT INTO RAW.AIR_WEATHER_RAW
        (region, latitude, longitude, collected_at,
         temperature_c, humidity_pct, wind_speed_kmh, pm2_5, pm10)
        VALUES (%(region)s, %(latitude)s, %(longitude)s, %(collected_at)s,
                %(temperature_c)s, %(humidity_pct)s, %(wind_speed_kmh)s,
                %(pm2_5)s, %(pm10)s)
    """
    cur.executemany(insert_sql, records)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(records)} records into Snowflake.")


# ---------------------------------------------------------------------------
# 4. MAIN: tie it together.
# ---------------------------------------------------------------------------
def main():
    print("Starting ingestion run...")
    records = []
    for region in REGIONS:
        try:
            record = fetch_region(region)
            records.append(record)
            print(f"  ✓ {region['name']}: "
                  f"{record['temperature_c']}°C, PM2.5={record['pm2_5']}")
        except Exception as e:
            # If one region fails, log it and keep going (don't crash the run).
            print(f"  ✗ {region['name']} failed: {e}")

    if records:
        load_to_snowflake(records)
    else:
        print("No records collected — nothing to load.")


if __name__ == "__main__":
    main()
