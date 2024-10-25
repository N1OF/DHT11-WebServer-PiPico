#main.py
#Private Open Source License 1.0
#Copyright 2024 Scott Sheets

#https://github.com/DomTheDorito/Private-Open-Source-License

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the 
#Software without limitation the rights to personally use, copy, modify, distribute,
#and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#2. The source code shall not be used for commercial purposes, including but not limited to sale of the Software, or use in products 
#intended for sale, unless express writen permission is given by the source creator.

#3. Attribution to source work shall be made plainly available in a reasonable manner.

#THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
#AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#THIS LICENSE MAY BE UPDATED OR REVISED, WITH NOTICE ON THE POS LICENSE REPOSITORY.

#DHT11-WebServer-PiPico
import machine
import network
import socket
import time
import dht

# Configuration
DHT_PIN = 8 # Replace with the pin you connected the DHT11 to
SSID = 'YourSSID'  # Replace with your Wi-Fi SSID
PASSWORD = 'YourPassword'  # Replace with your Wi-Fi password

# Initialize the DHT11 sensor
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Wait for connection
while not wlan.isconnected():
    print("Connecting to WiFi...")
    time.sleep(1)

print("Connected to WiFi:", wlan.ifconfig())

# Create a socket for the web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]  # Adjusted to only use address and port
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running at http://{}".format(addr))

def web_page(temperature, humidity):
    return """<!DOCTYPE html>
<html>
<head>
    <title>DHT11 Sensor Readings</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f2f2f2;
            margin: 0;
        }}
        .container {{
            text-align: center;
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            width: 300px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        h1 {{
            color: #333;
        }}
        p {{
            font-size: 1.2em;
            color: #555;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>DHT11 Sensor Readings</h1>
        <p>Temperature: {:.1f} °F</p>
        <p>Humidity: {:.1f} %</p>
    </div>
</body>
</html>
""".format(temperature, humidity)


while True:
    # Wait for a client to connect
    cl, addr = s.accept()
    print('Client connected from', addr)

    # Read the client request (optional debugging)
    request = cl.recv(1024)
    print("Request:", request)

    # Read temperature and humidity
    try:
        dht_sensor.measure()
        temp_c = dht_sensor.temperature()
        temperature = (temp_c * 1.8) + 32 # Converts C to F, comment out and replace temp_c in like 92 with temperature if not needed. Don't forget to edit the HTML <p> for C.
        humidity = dht_sensor.humidity()
    except OSError as e:
        print('Failed to read sensor:', e)
        temperature = None
        humidity = None

    # Handle None readings
    if temperature is None or humidity is None:
        response = "Error reading sensor data."
    else:
        response = web_page(temperature, humidity)

    # Send HTTP response to the client in one go
    http_response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' + response
    cl.sendall(http_response.encode('utf-8'))  # Send the full HTTP response
    cl.close()

    # Add a small delay to prevent overloading the sensor
    time.sleep(2)


