from flask import Flask, render_template, request
import requests

app = Flask(__name__)


ESP32_IP = "esp32-car"
ESP32_URL = f"http://{ESP32_IP}.local:80/control"

# Function to send commands to the ESP32
def send_car_command(command, speed):
    try:
        url = f"{ESP32_URL}?cmd={command}&speed={speed}"
        response = requests.get(url)
        print(f"Sent command: {command}, Speed: {speed}")
    except Exception as e:
        print(f"Error sending command: {e}")

# Route for the web interface
@app.route('/')
def index():
    return render_template('index.html')

# Route for controlling the car
@app.route('/control', methods=['GET'])
def control():
    cmd = request.args.get('cmd')
    speed = int(request.args.get('speed'))
    send_car_command(cmd, speed)
    return f"Command executed: {cmd} with speed {speed}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
