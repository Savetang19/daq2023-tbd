from machine import Pin, ADC, I2C
import _thread
import network
import time
import json
import uasyncio as asyncio
from math import log10
from umqtt.robust import MQTTClient
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS
)
import dht
import time

led_red = Pin(2, Pin.OUT)
led_red.value(1)  # turn the red led off
led_iot = Pin(12, Pin.OUT)
led_iot.value(1)   # turn the green led off
#connecting
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Connecting to WiFi")
wlan.connect(WIFI_SSID, WIFI_PASS)
while not wlan.isconnected():
    time.sleep(0.5)
print("Wifi connected")
led_red.value(0)

mqtt = MQTTClient(client_id="",
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)
print("Connecting to MQTT broker")
mqtt.connect()
print("MQTT broker connected")
led_iot.value(0)

moisture_sensor = ADC(Pin(32)) # I1
moisture_sensor.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT11(Pin(33)) # I2

class LinearInterpolation:
    def __init__(self, x0, x1, y0, y1, clip=True):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.clip = clip
        
    def map(self, y):
        if self.clip:
            x = max(y, self.y0)
            x = min(y, self.y1)
        return (y-self.y0)/(self.y1-self.y0)*(self.x1-self.x0) + self.x0

ldr = ADC(Pin(36))

converter = LinearInterpolation(log10(0.1),log10(10000),log10(1000),log10(0.1))

def V_ldr(adc):
    #12bit res
    adc_resolution = 4095
    v_range=1.1
    return (adc / adc_resolution) * v_range

def R_ldr(va):
    r1= 33000
    return (r1 * va) / (3.3 - va)

def Lux_meter():
    va = V_ldr(ldr.read())
    r_ldr = (R_ldr(va)/1000)
    lux=10**(converter.map(log10(r_ldr)))
    return lux

def moistmeter():
    moisture_value = moisture_sensor.read()
    moisture_percentage = (moisture_value / 4095) * 100
    return moisture_percentage

async def send_data():
    while True:
        await asyncio.sleep(0.01)
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        light = Lux_meter()
        moist = moistmeter()
        await asyncio.sleep(0.1)
        lt= {"lat":321,
             "lon":321,
             "light":light,
             "temp":temperature,
             "humid":humidity,
             "moisture":moist
            }
        print(lt)
        mqtt.publish("daq2023/group6/sensors", json.dumps(lt))
        await asyncio.sleep(1)


# while True:
#     moisture_value = moisture_sensor.read()
#     print("Moisture value:", moisture_value)
#     # mapping the ADC range (0-4095) to a percentage (0-100)
#     moisture_percentage = (moisture_value / 4095) * 100
#     print(f"Moisture percentage: {moisture_percentage: .2f}%")
#     dht_sensor.measure()
#     temperature = dht_sensor.temperature()
#     humidity = dht_sensor.humidity()
#     print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
#     print("---------------------------------------------------- ")
#     time.sleep(5)
async def check_msg_task():
    while True:
        mqtt.check_msg()
        await asyncio.sleep_ms(0)

asyncio.create_task(check_msg_task())
asyncio.create_task(send_data())
asyncio.run_until_complete()
