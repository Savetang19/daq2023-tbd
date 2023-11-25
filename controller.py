import sys
from flask import abort
import pymysql
from dbutils.pooled_db import PooledDB
from config import OPENAPI_STUB_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME

sys.path.append(OPENAPI_STUB_DIR)
from swagger_server import models

pool = PooledDB(creator=pymysql,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME,
                maxconnections=1,
                blocking=True)

WEATHER_CONDITIONS = {
    1: "Clear",
    2: "Partly cloudy",
    3: "Cloudy",
    4: "Overcast",
    5: "Light rain",
    6: 'Moderate rain',
    7: "Heavy rain",
    8: "Thunderstorm",
    9: "Very cold",
    10: "Cold",
    11: "Cool",
    12: "Very hot"
}

def get_table(location):
    """Return the table name for a given location."""
    if location == "indoor":
        return "kidbright_indoor"
    elif location == "outdoor":
        return "kidbright_outdoor"
    else:
        abort(400, "Invalid location {}".format(location))


def get_current_weather_data(location):
    """Return the most recent weather data for a given location."""
    table = get_table(location)
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT kb.temp, kb.humid, tmd.rain, tmd.cond
            FROM {table} kb, hpc_tmd tmd
            WHERE kb.ts = tmd.ts
            ORDER BY kb.ts DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
        result = models.WeatherData(*result)
        result.condition = WEATHER_CONDITIONS[result.condition]
    if result:
        return result
    else:
        abort(404)


def get_forecast_weather():
    """Return the forecast weather data for the next 3 hours."""
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT tc, rh, rain, cond 
            FROM hpc_tmd
            ORDER BY ts DESC
            LIMIT 2
                   """)
        result = [models.WeatherData(*row) for row in cs.fetchall()]
        for row in result:
            row.condition = WEATHER_CONDITIONS[row.condition]
    if result == []:
        abort(404)
    return result


def get_moisture_data(location):
    """"Return the most recent soil moisture data for a given location."""
    table = get_table(location)
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT moisture
            FROM {table}
            ORDER BY ts DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
    if result:
        return models.SoilMoistureData(*result)
    else:
        abort(404)
        

def get_watering_condition(location):
    """Return boolean value that calculate from 3 hour forecast weather condition, soil-moisture, and humidity."""
    table = get_table(location)
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT kb.moisture, kb.humid, tmd.cond
            FROM {table} kb, hpc_tmd tmd
            WHERE kb.ts = tmd.ts
            ORDER BY kb.ts DESC
        """)
        result = cs.fetchone()
    if result:
        return models.WateringCondition(*result)
    else:
        abort(404)


def get_recommend_roof_status(location):
    """"Returns String value that is calculated from forecast weather condition and rainfall sensor."""
    table = get_table(location)
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT
            CASE
                WHEN forecast_weather = 'rainy' AND rainfall > 5 THEN 'closed'
                ELSE 'open'
            END AS recommend_roof_status,
            current_timestamp AS timestamp,
            rainfall,
            condition
            FROM {table}
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
    if result:
        return models.RoofCondition(*result)
    else:
        abort(404)


def get_recommend_sunshade_status(location):
    """"Returns String value for sun shade  that is calculated from forecast weather condition and rainfall sensor."""
    table = get_table(location)
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT
            CASE
                WHEN forecast_weather = 'sunny' AND rainfall < 5 AND condition = 'clear' THEN 'open'
                ELSE 'closed'
            END AS recommend_sun_shade_status,
            current_timestamp AS timestamp,
            rainfall,
            condition
            FROM {table}
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
    if result:
        return models.SunShadeCondition(*result)
    else:
        abort(404)