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
            WHERE DATE_FORMAT(kb.ts, '%Y-%m-%d %H') = DATE_FORMAT(tmd.ts, '%Y-%m-%d %H')
            ORDER BY DATE_FORMAT(kb.ts, '%Y-%m-%d %H') DESC
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
            SELECT kb.ts, kb.humid, kb.moisture,tmd.cond
            FROM {table} kb, hpc_tmd tmd
            WHERE DATE_FORMAT(kb.ts, '%Y-%m-%d %H:00:00') = DATE_FORMAT(tmd.ts, '%Y-%m-%d %H:00:00')
            ORDER BY DATE_FORMAT(kb.ts, '%Y-%m-%d %H:00:00') DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
        if result == None:
            abort(404)
        # this for readable code you can change if want
        # result = tuple(ts, humidity, moisture, condition)
        ts = result[0]
        humidity = result[1]
        moisture = result[2]
        condition = result[3]
        model = models.WateringCondition(*result)
        if condition in [1, 2, 3, 4, 12] and moisture < 40 and humidity < 50:
            model.watering_needed = True
        else: # condition in [5, 6, 7, 8, 9, 10, 11]
            model.watering_needed = False
        model.timestamp = ts
        model.humidity = humidity
        model.moisture_threshold = moisture
        model.condition = WEATHER_CONDITIONS[condition]
    return model


def get_recommend_roof_status():
    """"Returns String value that is calculated from forecast weather condition and rainfall sensor."""
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
            FROM kidbright_indoor
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
    # TODO Please delete comment below.
    # I still don't know why we need outdoor in door cause we didn't use kidbright data to answer
    table = get_table(location)
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute(f"""
            SELECT kb.ts, tmd.cond, tmd.rain
            FROM {table} kb, hpc_tmd tmd
            WHERE DATE_FORMAT(kb.ts, '%Y-%m-%d %H:00:00') = DATE_FORMAT(tmd.ts, '%Y-%m-%d %H:00:00')
            ORDER BY DATE_FORMAT(kb.ts, '%Y-%m-%d %H:00:00') DESC
            LIMIT 1;
        """)
        result = cs.fetchone()
        if result == None:
            abort(404)
        # this for readable code you can change if want
        # result = tuple(ts, condition, rainfall)
        ts = result[0]
        condition = result[1]
        rainfall = result[2]
        model = models.SunShadeCondition(*result)
        # change if needed
        if condition in [1, 2, 3, 4, 12] and rainfall < 5:
            model.recommend_sun_shade_status = 'opened'
        else:
            model.recommend_sun_shade_status = 'closed'
        model.condition = WEATHER_CONDITIONS[condition]
        model.timestamp = ts
        model.rainfall = rainfall
    return model