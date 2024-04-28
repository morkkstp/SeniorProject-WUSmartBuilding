import machine
import gc
import utime
from machine import I2C, Pin
import adafruit_mlx90640
import network
import ntptime
import urequests
from ir_transmitter.ir_transmitter import irSelectCMD, irSendCMD

# Function to Get CurrentTime from NTP Server
def get_current_time():
    actual_time = utime.localtime(utime.time() + 25200)
    rtc = machine.RTC()
    rtc.datetime((actual_time[0], actual_time[1], actual_time[2], 0, actual_time[3], actual_time[4], actual_time[5], 0))
    t = rtc.datetime()
    return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])

# Function to Send Control Signal
def control_signal(signal_index, irLedPwmObject):
    irCMDList = irSelectCMD(signal_index)
    irSendCMD(irLedPwmObject, irCMDList, duty=360)

# Function to Initialize MLX90640
def init_mlx90640():
    i2c = I2C(0, scl=Pin(22, Pin.OUT), sda=Pin(21, Pin.OUT), freq=800000)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_1_HZ
    return mlx

# Function to Connect to Wi-Fi
def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('WiFi-Name', 'Password')
    return sta_if

# Function to Check and Reconnect Wi-Fi if Necessary
def check_wifi(sta_if, led_pin):
    while not sta_if.isconnected():
        led_pin.value(1)
        utime.sleep(0.2)
        led_pin.value(0)
        utime.sleep(0.2)
    led_pin.value(1)

# Function to Send Data to Firebase Realtime Database
def send_to_firebase(data, timestamp):
    firebase_url = 'URL-Firebase&Path'
    full_url = firebase_url + timestamp + '.json'
    chunk_size = 64
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    for i, chunk in enumerate(chunks):
        response = urequests.patch(full_url, json={i: chunk})
        response.close()

# Function to Get Prediction from External API
def get_prediction():
    response = urequests.get("URL-Firebase&Path")
    data = response.json()
    response.close()
    return data

# Set CPU Frequency
machine.freq(240000000)

# Set LED
led = machine.Pin(2, machine.Pin.OUT)

# Initialize MLX90640
mlx = init_mlx90640()

# Connect to Wi-Fi
sta_if = connect_wifi()
check_wifi(sta_if, led)

# Initialize IR LED PWM Object
irLedPwmObject = machine.PWM(machine.Pin(17, machine.Pin.OUT), freq=38000, duty=0)

gc.enable()
num_none = 0
while True:
    try:
        utime.sleep(60)
        ntptime.settime()
        timestamp = get_current_time()
        frame = [0] * 768
        mlx.getFrame(frame)
        send_to_firebase(frame, timestamp)
        frame = None
        timestamp = None
        utime.sleep(2)
        data = get_prediction()
        message_predicted = data.get('message', {}).get('result', None)
        if message_predicted == 0:
            num_none += 1
            if num_none == 3:
                control_signal(0, irLedPwmObject)
                control_signal(1, irLedPwmObject)
                print("0")
                num_none = 0
        elif message_predicted == 1:
            print("1")
            num_none = 0
        elif message_predicted == 2:
            control_signal(1, irLedPwmObject)
            utime.sleep(1)
            control_signal(2, irLedPwmObject)
            utime.sleep(1)
            control_signal(3, irLedPwmObject)
            print("2")
            num_none = 0

    except Exception as e:
        print(f"Error: {e}")
        machine.reset()
